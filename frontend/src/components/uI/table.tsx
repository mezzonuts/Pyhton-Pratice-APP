// @ts-nocheck
import * as React from 'react'

export const Table = ({ children }: { children: React.ReactNode }) => (
  <div className="w-full overflow-x-auto"><table className="w-full text-sm">{children}</table></div>
)
export const TableHeader = ({ children }: { children: React.ReactNode }) => (
  <thead className="border-b font-medium">{children}</thead>
)
export const TableRow = ({ children }: { children: React.ReactNode }) => (
  <tr className="border-b">{children}</tr>
)
export const TableCell = ({ children }: { children: React.ReactNode }) => (
  <td className="p-3">{children}</td>
)
