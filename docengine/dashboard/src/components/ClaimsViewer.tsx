import React from 'react';
import { ClaimItem, VerificationDetail } from '@/types/docengine';
export function ClaimsViewer({ claims, verificationDetails }: { claims: ClaimItem, verificationDetails?: VerificationDetail }) {
  return (
    <div className="mt-4 border-t border-border pt-3 text-xs">
      <div className="font-semibold text-muted mb-2 uppercase tracking-wider">Declaraciones vs Verificación</div>
      <div className="space-y-2">
        <div>
          <span className="text-muted">Archivos Modificados:</span>
          {claims.files_modified.length === 0 ? <span className="text-muted italic ml-2">[NINGUNO]</span> : (
            <ul className="ml-4 mt-1 space-y-1">
              {claims.files_modified.map((file, idx) => {
                const status = verificationDetails?.files.find((f) => f.file === file)?.status;
                return (
                  <li key={idx} className="flex items-center space-x-2">
                    <span className="text-text font-mono">{file}</span>
                    {status && <span className={`text-[10px] px-1.5 py-0.2 rounded ${status === 'VERIFICADO' ? 'bg-green-900 text-ok' : 'bg-red-900 text-error font-bold'}`}>{status}</span>}
                  </li>
                );
              })}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
