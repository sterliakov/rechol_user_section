export function toStartOfDay<DateType extends Date | string>(date: DateType): DateType {
  const output = new Date(date);
  output.setHours(0, 0, 0, 0);

  return (typeof date === 'string' ? output.toISOString() : output) as DateType;
}

export function toEndOfDay<DateType extends Date | string>(date: DateType): DateType {
  const output = new Date(date);
  output.setHours(23, 59, 59, 999);

  return (typeof date === 'string' ? output.toISOString() : output) as DateType;
}
