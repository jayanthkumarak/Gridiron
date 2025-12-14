// API client for Gridiron backend

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface AnalyzeRequest {
	query: string;
}

export interface ChartConfig {
	type: 'dot' | 'slope' | 'sparkline' | 'bar';
	title: string;  // Chart title for context
	data: Array<{ name: string; value: number; category?: string }>;
	xLabel?: string;
	yLabel?: string;
}

export interface AnalyzeResponse {
	headline: string;
	summary: string;
	// Support both single chart (legacy) and multiple charts
	chart?: ChartConfig;
	charts?: ChartConfig[];  // Multiple charts for comprehensive analysis
	insights?: string[];     // Key insights/takeaways
	raw_data?: Record<string, unknown>;
	error?: string;
}

export async function analyzeQuery(query: string): Promise<AnalyzeResponse> {
	const response = await fetch(`${API_BASE}/analyze`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
		},
		body: JSON.stringify({ query }),
	});

	if (!response.ok) {
		throw new Error(`API error: ${response.status}`);
	}

	return response.json();
}

export async function checkHealth(): Promise<boolean> {
	try {
		const response = await fetch(`${API_BASE}/health`);
		return response.ok;
	} catch {
		return false;
	}
}
