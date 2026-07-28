import React from 'react';
export function StatusBadge({ status }: { status: string }) {
  let colorClass = 'bg-gray-800 text-gray-300 border-gray-700';
  if (status === 'VERIFICADO' || status === 'COMPLETADO') colorClass = 'bg-green-950 text-ok border-ok';
  else if (status === 'DISCREPANCIA' || status === 'BLOQUEADO') colorClass = 'bg-red-950 text-error border-error font-bold animate-pulse';
  else if (status === 'PARCIAL' || status === 'NO_ENCONTRADO') colorClass = 'bg-yellow-950 text-warn border-warn';
  return <span className={`px-2 py-0.5 text-xs border rounded uppercase tracking-wider ${colorClass}`}>{status || '[FALTA ESTADO]'}</span>;
}
