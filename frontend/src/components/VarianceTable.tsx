import React from 'react';
import { motion } from 'framer-motion';

interface VarianceTableProps {
  data: Array<Record<string, string>>;
}

export const VarianceTable: React.FC<VarianceTableProps> = ({ data }) => {
  if (!data || data.length === 0) {
    return (
      <div className="swag-card text-center py-12">
        <p className="text-swag-skull-white/50">No data available</p>
      </div>
    );
  }

  const columns = ['vendor_sku', 'description', 'unit_cost', 'variance_flag', 'variance_%', 'processed_date'];
  const displayColumns = columns.filter(col => data[0]?.[col] !== undefined);

  return (
    <div className="swag-card overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b-2 border-swag-neon-green/30">
            {displayColumns.map((col) => (
              <th
                key={col}
                className="px-4 py-3 text-left text-sm font-bold text-swag-neon-green uppercase tracking-wide"
              >
                {col.replace('_', ' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, index) => (
            <motion.tr
              key={index}
              className="border-b border-swag-dark-tertiary hover:bg-swag-neon-green/5 transition-colors"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              {displayColumns.map((col) => (
                <td key={col} className="px-4 py-3 text-sm">
                  {col === 'variance_flag' ? (
                    <span className="text-xl">{row[col]}</span>
                  ) : (
                    <span className="text-swag-skull-white/90">{row[col]}</span>
                  )}
                </td>
              ))}
            </motion.tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
