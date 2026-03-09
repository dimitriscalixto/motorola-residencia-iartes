import { useCallback, useEffect, useMemo, useState } from "react";

type ScanStatus = "queued" | "running" | "completed" | "failed";

type ScanExecution = {
  id: number;
  source_name: string;
  source_url: string;
  status: ScanStatus;
  started_at: string | null;
  finished_at: string | null;
  discovered_links_count: number;
  valid_topics_count: number;
  processed_topics_count: number;
  failed_topics_count: number;
  created_at: string;
  updated_at: string;
};

type ScanStartResponse = {
  message: string;
  scan_execution: ScanExecution;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
const FIXED_SOURCE_URL = "https://forums.lenovo.com/t5/Motorola-Community/ct-p/MotorolaCommunity";

function getStatusLabel(status: ScanStatus | null): string {
  if (status === null) {
    return "Sem execucao ainda";
  }
  if (status === "queued") {
    return "Na fila";
  }
  if (status === "running") {
    return "Executando";
  }
  if (status === "completed") {
    return "Concluida";
  }
  return "Falhou";
}

async function fetchLatestScan(): Promise<ScanExecution | null> {
  const response = await fetch(`${API_BASE_URL}/scan/latest`);
  if (!response.ok) {
    throw new Error(`Falha ao consultar ultima execucao (${response.status})`);
  }
  return (await response.json()) as ScanExecution | null;
}

async function startScan(): Promise<ScanExecution> {
  const response = await fetch(`${API_BASE_URL}/scan/start`, { method: "POST" });
  if (!response.ok) {
    throw new Error(`Falha ao iniciar varredura (${response.status})`);
  }
  const payload = (await response.json()) as ScanStartResponse;
  return payload.scan_execution;
}

function App() {
  const [scan, setScan] = useState<ScanExecution | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadLatestScan = useCallback(async () => {
    try {
      const latest = await fetchLatestScan();
      setScan(latest);
      setErrorMessage(null);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erro ao consultar execucao";
      setErrorMessage(message);
    }
  }, []);

  useEffect(() => {
    void loadLatestScan();
    const intervalId = window.setInterval(() => {
      void loadLatestScan();
    }, 5000);
    return () => window.clearInterval(intervalId);
  }, [loadLatestScan]);

  const statusLabel = useMemo(() => getStatusLabel(scan?.status ?? null), [scan?.status]);

  const handleStartScan = useCallback(async () => {
    setIsStarting(true);
    setErrorMessage(null);
    try {
      const startedScan = await startScan();
      setScan(startedScan);
      await loadLatestScan();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Erro ao iniciar varredura";
      setErrorMessage(message);
    } finally {
      setIsStarting(false);
    }
  }, [loadLatestScan]);

  return (
    <main className="page">
      <section className="hero">
        <h1>Motorola Community Scanner</h1>
        <p>Varredura automatizada da comunidade Motorola no forum da Lenovo.</p>
        <button type="button" className="primary-action" onClick={() => void handleStartScan()} disabled={isStarting}>
          {isStarting ? "Iniciando..." : "Iniciar varredura da comunidade Motorola"}
        </button>
        <small>Fonte fixa: {scan?.source_url ?? FIXED_SOURCE_URL}</small>
        {errorMessage && <p className="error">{errorMessage}</p>}
      </section>

      <section className="stats">
        <h2>Resumo da Ultima Execucao</h2>
        <div className="grid">
          <article>
            <h3>Status</h3>
            <p>{statusLabel}</p>
          </article>
          <article>
            <h3>Links descobertos</h3>
            <p>{scan?.discovered_links_count ?? 0}</p>
          </article>
          <article>
            <h3>Topicos validos</h3>
            <p>{scan?.valid_topics_count ?? 0}</p>
          </article>
          <article>
            <h3>Processados</h3>
            <p>{scan?.processed_topics_count ?? 0}</p>
          </article>
          <article>
            <h3>Falhas</h3>
            <p>{scan?.failed_topics_count ?? 0}</p>
          </article>
        </div>
      </section>
    </main>
  );
}

export default App;
