"""
Variance Intelligence Engine (V2) for Swag Golf Pricing Intelligence Tool
Data-scientist grade variance analysis with rolling averages, supplier baselines,
and cost impact scoring for business decision support.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional
from datetime import datetime


class VarianceEngine:
    """
    Analyzes pricing variance using rolling statistics and supplier baselines.
    Provides intelligent flagging based on impact and historical patterns.
    """

    def __init__(self, green_threshold: float = 3.0, yellow_threshold: float = 10.0,
                 rolling_window: int = 3, supplier_window: int = 30):
        """
        Initialize Variance Intelligence Engine.

        Args:
            green_threshold: Variance % threshold for green flag (default 3.0%)
            yellow_threshold: Variance % threshold for yellow flag (default 10.0%)
            rolling_window: Number of historical records for rolling average (default 3)
            supplier_window: Number of supplier records for baseline (default 30)
        """
        self.green_threshold = green_threshold
        self.yellow_threshold = yellow_threshold
        self.rolling_window = rolling_window
        self.supplier_window = supplier_window

    def load_historical_data(self, sheets_service, sheet_id: str, sheet_name: str) -> pd.DataFrame:
        """
        Load all historical data from Google Sheets.

        Args:
            sheets_service: Google Sheets API service instance
            sheet_id: Google Sheets spreadsheet ID
            sheet_name: Sheet tab name

        Returns:
            DataFrame with historical pricing data

        Raises:
            Exception: If sheet read fails
        """
        try:
            # Read all data from sheet
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=sheet_id,
                range=f"{sheet_name}!A:Z"
            ).execute()

            values = result.get('values', [])

            if not values:
                print("📊 No historical data found in sheet (empty sheet)")
                return pd.DataFrame()

            # First row is headers
            headers = values[0]
            data_rows = values[1:] if len(values) > 1 else []

            print(f"   Found {len(headers)} column headers")
            print(f"   Found {len(data_rows)} data rows")

            if not data_rows:
                print("📊 Sheet has headers but no data rows")
                return pd.DataFrame(columns=headers)

            # Ensure all rows have same number of columns as headers
            padded_rows = []
            for idx, row in enumerate(data_rows):
                original_len = len(row)
                # Pad short rows with empty strings
                if len(row) < len(headers):
                    row = list(row) + [''] * (len(headers) - len(row))
                # Trim long rows to match headers
                elif len(row) > len(headers):
                    if idx == 0:  # Only log once
                        print(f"   ⚠️  Data rows have {original_len} columns, trimming to {len(headers)}")
                    row = list(row[:len(headers)])
                else:
                    row = list(row)
                padded_rows.append(row)

            # Create DataFrame
            try:
                df = pd.DataFrame(padded_rows, columns=headers)
            except Exception as e:
                print(f"   ❌ DataFrame creation error: {e}")
                print(f"   Headers ({len(headers)}): {headers}")
                print(f"   First row ({len(padded_rows[0])}): {padded_rows[0]}")
                raise

            # Convert numeric columns
            numeric_cols = ['quantity', 'unit_cost', 'total_cost', 'variance_%',
                          'supplier_baseline_%', 'impact_$']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # Convert date columns
            if 'processed_date' in df.columns:
                df['processed_date'] = pd.to_datetime(df['processed_date'], errors='coerce')

            print(f"✅ Loaded {len(df)} historical rows from Google Sheet")

            return df

        except Exception as e:
            raise Exception(f"Failed to load historical data: {e}")

    def calculate_rolling_statistics(self, historical_df: pd.DataFrame,
                                     new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate rolling average and median for each SKU.

        Args:
            historical_df: Historical pricing data
            new_df: New invoice data to annotate

        Returns:
            new_df with rolling statistics added
        """
        if historical_df.empty:
            print("⚠️  No historical data for rolling statistics")
            new_df['rolling_avg_cost'] = None
            new_df['rolling_median_cost'] = None
            new_df['last_cost'] = None
            return new_df

        # Combine historical and new data for each SKU
        rolling_stats = []

        for idx, row in new_df.iterrows():
            sku = row['vendor_sku']

            # Get historical records for this SKU
            sku_history = historical_df[historical_df['vendor_sku'] == sku].copy()

            if sku_history.empty:
                rolling_stats.append({
                    'rolling_avg_cost': None,
                    'rolling_median_cost': None,
                    'last_cost': None
                })
                continue

            # Sort by processed_date
            sku_history = sku_history.sort_values('processed_date', ascending=True)

            # Get last N records for rolling window
            recent_records = sku_history.tail(self.rolling_window)

            # Calculate rolling statistics
            unit_costs = recent_records['unit_cost'].dropna()

            if len(unit_costs) > 0:
                rolling_avg = unit_costs.mean()
                rolling_median = unit_costs.median()
                last_cost = unit_costs.iloc[-1]  # Most recent cost
            else:
                rolling_avg = None
                rolling_median = None
                last_cost = None

            rolling_stats.append({
                'rolling_avg_cost': rolling_avg,
                'rolling_median_cost': rolling_median,
                'last_cost': last_cost
            })

        # Add to new_df
        stats_df = pd.DataFrame(rolling_stats)
        new_df = pd.concat([new_df.reset_index(drop=True), stats_df], axis=1)

        skus_with_history = new_df['rolling_avg_cost'].notna().sum()
        print(f"✅ Calculated rolling averages for {skus_with_history} SKU(s)")

        return new_df

    def calculate_supplier_baseline(self, historical_df: pd.DataFrame,
                                    new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate supplier-level baseline variance percentage.

        Args:
            historical_df: Historical pricing data
            new_df: New invoice data to annotate

        Returns:
            new_df with supplier baseline added
        """
        if historical_df.empty:
            print("⚠️  No historical data for supplier baselines")
            new_df['supplier_baseline_%'] = None
            return new_df

        supplier_baselines = []

        for idx, row in new_df.iterrows():
            supplier = row['supplier']

            if pd.isna(supplier) or supplier == '':
                supplier_baselines.append(None)
                continue

            # Get supplier historical records
            supplier_history = historical_df[historical_df['supplier'] == supplier].copy()

            # Limit to last N records
            supplier_history = supplier_history.tail(self.supplier_window)

            # Calculate variance percentages from historical data
            variances = supplier_history['variance_%'].dropna()

            if len(variances) >= 3:  # Need at least 3 records
                baseline = variances.abs().mean()
            else:
                baseline = None

            supplier_baselines.append(baseline)

        new_df['supplier_baseline_%'] = supplier_baselines

        suppliers_with_baseline = new_df['supplier_baseline_%'].notna().sum()
        print(f"✅ Applied supplier baselines for {suppliers_with_baseline} row(s)")

        return new_df

    def calculate_variance_and_impact(self, new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate variance percentages and impact scores.

        Args:
            new_df: New invoice data with rolling statistics

        Returns:
            new_df with variance_%, impact_$, and impact_score added
        """
        variances = []
        impacts_dollar = []
        impact_scores = []

        for idx, row in new_df.iterrows():
            current_cost = row['unit_cost']
            rolling_avg = row.get('rolling_avg_cost')
            last_cost = row.get('last_cost')
            quantity = row['quantity']

            # Calculate variance
            if pd.notna(rolling_avg) and rolling_avg > 0 and pd.notna(current_cost):
                # Use rolling average for variance calculation
                variance_pct = ((current_cost - rolling_avg) / rolling_avg) * 100
                variance_pct = round(variance_pct, 2)
            elif pd.notna(last_cost) and last_cost > 0 and pd.notna(current_cost):
                # Fallback to basic variance if no rolling avg
                variance_pct = ((current_cost - last_cost) / last_cost) * 100
                variance_pct = round(variance_pct, 2)
            else:
                variance_pct = None

            # Calculate impact in dollars
            if pd.notna(last_cost) and pd.notna(current_cost) and pd.notna(quantity):
                impact_dollar = (current_cost - last_cost) * quantity
                impact_dollar = round(impact_dollar, 2)
            else:
                impact_dollar = None

            # Calculate impact score (for prioritization)
            if pd.notna(variance_pct) and pd.notna(quantity):
                impact_score = abs(variance_pct) * quantity
            else:
                impact_score = None

            variances.append(variance_pct)
            impacts_dollar.append(impact_dollar)
            impact_scores.append(impact_score)

        new_df['variance_%'] = variances
        new_df['impact_$'] = impacts_dollar
        new_df['_impact_score'] = impact_scores  # Internal use for sorting

        print(f"✅ Calculated variance and impact scores for {len(new_df)} row(s)")

        return new_df

    def assign_variance_flags(self, new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Assign variance flags based on thresholds.

        Args:
            new_df: New invoice data with variance_% calculated

        Returns:
            new_df with variance_flag added
        """
        flags = []

        for idx, row in new_df.iterrows():
            variance = row.get('variance_%')

            if pd.isna(variance):
                # No historical data
                flags.append('')
                continue

            abs_variance = abs(variance)

            if abs_variance <= self.green_threshold:
                flags.append('🟢')
            elif abs_variance <= self.yellow_threshold:
                flags.append('🟡')
            else:
                flags.append('🔴')

        new_df['variance_flag'] = flags

        # Count flags
        flag_counts = new_df['variance_flag'].value_counts()
        print(f"✅ Assigned flags: ", end="")
        for flag, count in flag_counts.items():
            if flag:  # Skip empty strings
                print(f"{flag} {count} ", end="")
        print()

        return new_df

    def prioritize_high_impact(self, new_df: pd.DataFrame) -> pd.DataFrame:
        """
        Sort high-impact red flags to the top and log them.

        Args:
            new_df: New invoice data with flags and impact scores

        Returns:
            new_df sorted by priority
        """
        # Identify red flags
        red_flags = new_df[new_df['variance_flag'] == '🔴'].copy()

        if not red_flags.empty:
            # Sort by impact_$ descending
            red_flags = red_flags.sort_values('impact_$', ascending=False)

            print(f"\n🔺 HIGH-IMPACT VARIANCES DETECTED:")
            for idx, row in red_flags.iterrows():
                sku = row['vendor_sku']
                variance = row['variance_%']
                impact = row['impact_$']
                sign = '+' if variance > 0 else ''
                print(f"   SKU {sku}: {sign}{variance}%, ${sign}{impact:.2f} impact")

            # Rebuild dataframe with red flags first
            other_flags = new_df[new_df['variance_flag'] != '🔴']
            new_df = pd.concat([red_flags, other_flags], ignore_index=True)

        # Drop internal impact_score column
        if '_impact_score' in new_df.columns:
            new_df = new_df.drop(columns=['_impact_score'])

        # Drop temporary rolling columns
        temp_cols = ['rolling_avg_cost', 'rolling_median_cost', 'last_cost']
        for col in temp_cols:
            if col in new_df.columns:
                new_df = new_df.drop(columns=[col])

        return new_df

    def annotate_invoice_data(self, new_df: pd.DataFrame, sheets_service,
                              sheet_id: str, sheet_name: str) -> pd.DataFrame:
        """
        Main method to annotate new invoice data with variance intelligence.

        Process:
        1. Load historical data from Google Sheets
        2. Calculate rolling statistics per SKU
        3. Calculate supplier baselines
        4. Calculate variance percentages and impact scores
        5. Assign variance flags
        6. Prioritize high-impact items

        Args:
            new_df: New invoice data to annotate
            sheets_service: Google Sheets API service
            sheet_id: Google Sheets spreadsheet ID
            sheet_name: Sheet tab name

        Returns:
            Annotated DataFrame ready for appending to Google Sheets
        """
        print("\n" + "=" * 80)
        print("VARIANCE INTELLIGENCE ENGINE (V2)")
        print("=" * 80)

        # Step 1: Load historical data
        print("\n📊 Loading historical data from Google Sheets...")
        historical_df = self.load_historical_data(sheets_service, sheet_id, sheet_name)

        # Step 2: Calculate rolling statistics
        print("\n📈 Calculating rolling averages and medians...")
        new_df = self.calculate_rolling_statistics(historical_df, new_df)

        # Step 3: Calculate supplier baselines
        print("\n🏢 Calculating supplier-level baselines...")
        new_df = self.calculate_supplier_baseline(historical_df, new_df)

        # Step 4: Calculate variance and impact
        print("\n🧮 Calculating variance percentages and impact scores...")
        new_df = self.calculate_variance_and_impact(new_df)

        # Step 5: Assign flags
        print("\n🚦 Assigning variance flags...")
        new_df = self.assign_variance_flags(new_df)

        # Step 6: Prioritize high impact
        print("\n🎯 Prioritizing high-impact variances...")
        new_df = self.prioritize_high_impact(new_df)

        print("\n" + "=" * 80)
        print(f"✅ Variance analysis complete: {len(new_df)} annotated rows ready")
        print("=" * 80 + "\n")

        return new_df


def test_variance_engine():
    """Test variance engine with sample data."""
    print("=" * 80)
    print("VARIANCE ENGINE TEST")
    print("=" * 80)

    # Create sample historical data
    historical_data = pd.DataFrame({
        'vendor_sku': ['SKU001', 'SKU001', 'SKU001', 'SKU002', 'SKU002'],
        'unit_cost': [10.0, 10.5, 11.0, 5.0, 5.2],
        'supplier': ['SupplierA', 'SupplierA', 'SupplierA', 'SupplierB', 'SupplierB'],
        'processed_date': pd.to_datetime([
            '2024-01-01', '2024-01-15', '2024-02-01', '2024-01-10', '2024-02-05'
        ]),
        'variance_%': [None, 5.0, 4.76, None, 4.0]
    })

    # Create sample new data
    new_data = pd.DataFrame({
        'vendor_sku': ['SKU001', 'SKU002', 'SKU003'],
        'description': ['Item 1', 'Item 2', 'Item 3'],
        'quantity': [100, 50, 25],
        'unit_cost': [12.0, 5.1, 8.0],
        'total_cost': [1200.0, 255.0, 200.0],
        'supplier': ['SupplierA', 'SupplierB', 'SupplierC'],
        'invoice_number': ['INV001', 'INV002', 'INV003'],
        'invoice_date': ['2024-03-01', '2024-03-01', '2024-03-01'],
        'source_file': ['test.pdf', 'test.pdf', 'test.pdf'],
        'processed_date': ['2024-03-01 10:00:00', '2024-03-01 10:00:00', '2024-03-01 10:00:00']
    })

    # Initialize engine
    engine = VarianceEngine(green_threshold=3.0, yellow_threshold=10.0)

    # Simulate annotation (without Google Sheets)
    print("\nCalculating rolling statistics...")
    new_data = engine.calculate_rolling_statistics(historical_data, new_data)

    print("\nCalculating supplier baselines...")
    new_data = engine.calculate_supplier_baseline(historical_data, new_data)

    print("\nCalculating variance and impact...")
    new_data = engine.calculate_variance_and_impact(new_data)

    print("\nAssigning flags...")
    new_data = engine.assign_variance_flags(new_data)

    print("\nPrioritizing high impact...")
    new_data = engine.prioritize_high_impact(new_data)

    print("\nAnnotated Data:")
    print(new_data[['vendor_sku', 'unit_cost', 'variance_%', 'variance_flag',
                    'supplier_baseline_%', 'impact_$']].to_string(index=False))

    print("\n✅ Test complete")


if __name__ == "__main__":
    test_variance_engine()
