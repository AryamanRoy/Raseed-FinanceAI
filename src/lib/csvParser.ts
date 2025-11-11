export interface Transaction {
  id: string;
  date: Date;
  description: string;
  amount: number;
  category: string;
  paymentMethod: string;
}

export const parseCSV = (csvText: string): Transaction[] => {
  const lines = csvText.trim().split('\n');
  if (lines.length < 2) return [];

  // Skip header row
  const dataLines = lines.slice(1);
  const transactions: Transaction[] = [];

  dataLines.forEach((line, index) => {
    // Handle CSV parsing with quotes and commas
    const columns: string[] = [];
    let current = '';
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        columns.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    columns.push(current.trim()); // Push last column

    if (columns.length >= 5) {
      const [dateStr, description, amountStr, paymentMethod, category] = columns;
      
      // Parse date (DD-MM-YYYY format)
      const dateParts = dateStr.trim().split('-');
      if (dateParts.length === 3) {
        const day = parseInt(dateParts[0], 10);
        const month = parseInt(dateParts[1], 10);
        const year = parseInt(dateParts[2], 10);
        const date = new Date(year, month - 1, day);

        // Parse amount - remove any commas or spaces
        const cleanAmountStr = amountStr.trim().replace(/[,\s]/g, '');
        const amount = parseFloat(cleanAmountStr) || 0;

        if (!isNaN(date.getTime()) && !isNaN(amount) && amount > 0) {
          transactions.push({
            id: `txn-${index}-${Date.now()}`,
            date,
            description: description.trim(),
            amount,
            category: category.trim(),
            paymentMethod: paymentMethod.trim(),
          });
        }
      }
    }
  });

  return transactions;
};

export const getTransactionsForMonth = (
  transactions: Transaction[],
  month: number,
  year: number
): Transaction[] => {
  return transactions.filter(txn => {
    const txnMonth = txn.date.getMonth();
    const txnYear = txn.date.getFullYear();
    return txnMonth === month && txnYear === year;
  });
};

export const getTransactionsByCategory = (transactions: Transaction[]) => {
  const categoryMap = new Map<string, number>();
  
  transactions.forEach(txn => {
    const current = categoryMap.get(txn.category) || 0;
    categoryMap.set(txn.category, current + txn.amount);
  });

  return Array.from(categoryMap.entries()).map(([category, amount]) => ({
    category,
    amount,
  }));
};

// Determine if a transaction is income based on description
const isIncome = (description: string): boolean => {
  const incomeKeywords = ['salary', 'income', 'refund'];
  // Check for "Company Salary" or similar patterns
  const lowerDesc = description.toLowerCase();
  return incomeKeywords.some(keyword => lowerDesc.includes(keyword)) ||
         (lowerDesc.includes('company') && lowerDesc.includes('salary'));
};

export const getTotalIncome = (transactions: Transaction[]): number => {
  return transactions
    .filter(txn => isIncome(txn.description))
    .reduce((sum, txn) => sum + txn.amount, 0);
};

export const getTotalExpenses = (transactions: Transaction[]): number => {
  return transactions
    .filter(txn => !isIncome(txn.description))
    .reduce((sum, txn) => sum + txn.amount, 0);
};

export const getCategoryColor = (category: string): string => {
  const colors: Record<string, string> = {
    Food: '#FF6B6B',
    Groceries: '#96CEB4',
    Entertainment: '#45B7D1',
    Shopping: '#FFEAA7',
    Utilities: '#4ECDC4',
    Travel: '#DDA0DD',
    Bills: '#FFA07A',
    Fuel: '#F4A460',
    Other: '#A0A0A0',
  };
  return colors[category] || '#A0A0A0';
};

