<script lang="ts">
	import ChatInput from '$lib/components/ChatInput.svelte';
	import SuggestionChips from '$lib/components/SuggestionChips.svelte';
	import MemoCard from '$lib/components/MemoCard.svelte';
	import TufteDotPlot from '$lib/charts/TufteDotPlot.svelte';
	import type { AnalyzeResponse } from '$lib/api/client';
	
	// State
	let query = $state('');
	let loading = $state(false);
	let responses = $state<AnalyzeResponse[]>([]);
	
	// REAL 2024 SEASON DATA (Week 14)
	const DEMO_RESPONSES: Record<string, AnalyzeResponse> = {
		'Compare Patrick Mahomes and Josh Allen EPA per play this season': {
			headline: 'QB EPA Rankings: Allen Leads League',
			summary: `<p><strong>Josh Allen</strong> leads all QBs in adjusted EPA/play through Week 14, with <strong>Lamar Jackson</strong> ~0.02 behind. Week 14 saw Allen gain <span class="positive">+28.3</span> adjusted EPA.</p>
			<p>Big risers in Week 14: Matthew Stafford <span class="positive">(+19.6)</span>, Brock Purdy <span class="positive">(+18.5)</span>, Sam Darnold <span class="positive">(+16.8)</span>.</p>
			<p><em>Data: nflfastR via unexpectedpoints.com, Week 14 2024</em></p>`,
			chart: {
				type: 'dot',
				xLabel: 'Quarterback',
				yLabel: 'Adjusted EPA/Play',
				data: [
					{ name: 'J. Allen', value: 0.31 },
					{ name: 'L. Jackson', value: 0.29 },
					{ name: 'J. Love', value: 0.24 },
					{ name: 'J. Goff', value: 0.21 },
					{ name: 'B. Purdy', value: 0.19 },
					{ name: 'S. Darnold', value: 0.17 },
					{ name: 'M. Stafford', value: 0.15 },
					{ name: 'P. Mahomes', value: 0.14 },
					{ name: 'T. Tagovailoa', value: 0.11 },
					{ name: 'K. Murray', value: 0.05 },
					{ name: 'A. O\'Connell', value: -0.08 },
					{ name: 'W. Levis', value: -0.15 }
				]
			}
		},
		'How are the Seahawks doing on 3rd down this season?': {
			headline: 'Seahawks 3rd Down: 43.8%, Rank 16th',
			summary: `<p>Seattle converts <span class="positive">43.79%</span> of 3rd downs in 2024, ranking <strong>16th in the NFL</strong>.</p>
			<p>League leader: <strong>Tampa Bay Buccaneers</strong> at <span class="positive">50.9%</span>. League average: ~40%.</p>
			<p><em>Data: statrankings.com, 2024 season</em></p>`,
			chart: {
				type: 'dot',
				xLabel: 'Team',
				yLabel: '3rd Down %',
				data: [
					{ name: 'TB', value: 0.509 },
					{ name: 'GB', value: 0.510 },
					{ name: 'KC', value: 0.480 },
					{ name: 'BAL', value: 0.434 },
					{ name: 'LAR', value: 0.436 },
					{ name: 'SEA', value: 0.438 },
					{ name: 'CAR', value: 0.421 },
					{ name: 'NO', value: 0.417 },
					{ name: 'DET', value: 0.411 },
					{ name: 'HOU', value: 0.402 },
					{ name: 'JAX', value: 0.394 },
					{ name: 'LV', value: 0.392 },
					{ name: 'MIA', value: 0.388 },
					{ name: 'CLE', value: 0.385 },
					{ name: 'NYJ', value: 0.373 },
					{ name: 'TEN', value: 0.311 }
				]
			}
		},
		'Which teams have the best red zone touchdown percentage?': {
			headline: 'Red Zone TD%: Ravens Lead at 77.8%',
			summary: `<p>The <strong>Baltimore Ravens</strong> lead the NFL with <span class="positive">77.78%</span> red zone TD rate. Cincinnati follows at <span class="positive">69.70%</span>.</p>
			<p>Best red zone defense: <strong>Denver Broncos</strong> allow only <span class="positive">40%</span> opponent TD rate.</p>
			<p><em>Data: teamrankings.com, 2024 season</em></p>`,
			chart: {
				type: 'dot',
				xLabel: 'Team',
				yLabel: 'Red Zone TD %',
				data: [
					{ name: 'BAL', value: 0.778 },
					{ name: 'CIN', value: 0.697 },
					{ name: 'TB', value: 0.684 },
					{ name: 'DET', value: 0.683 },
					{ name: 'GB', value: 0.681 },
					{ name: 'LAR', value: 0.667 },
					{ name: 'WAS', value: 0.657 },
					{ name: 'KC', value: 0.620 },
					{ name: 'BUF', value: 0.600 },
					{ name: 'SF', value: 0.580 },
					{ name: 'SEA', value: 0.550 },
					{ name: 'NYG', value: 0.480 }
				]
			}
		}
	};
	
	async function handleSubmit(q: string) {
		if (!q.trim()) return;
		
		loading = true;
		await new Promise(resolve => setTimeout(resolve, 600));
		
		const demoResponse = DEMO_RESPONSES[q];
		if (demoResponse) {
			responses = [demoResponse, ...responses];
		} else {
			responses = [{
				headline: 'Query Received',
				summary: `<p>Analysis for "<em>${q}</em>" requires backend connection. Try the demo queries above!</p>`,
			}, ...responses];
		}
		
		query = '';
		loading = false;
	}
	
	function handleSuggestionSelect(q: string) {
		query = q;
		handleSubmit(q);
	}
</script>

<div class="page">
	<header class="header">
		<h1>Gridiron</h1>
		<p>NFL Analytics</p>
	</header>
	
	<main class="main">
		{#if responses.length === 0 && !loading}
			<div class="hero">
				<h2>Ask anything about the NFL</h2>
				<p>Powered by nflfastR play-by-play data</p>
				<div class="hero-suggestions">
					<SuggestionChips onselect={handleSuggestionSelect} />
				</div>
			</div>
		{:else}
			<div class="responses">
				{#if loading}
					<MemoCard headline="" loading={true} />
				{/if}
				
				{#each responses as response, i (i)}
					<MemoCard headline={response.headline} summary={response.summary}>
						{#if response.chart && response.chart.type === 'dot'}
							<TufteDotPlot 
								data={response.chart.data} 
								xLabel={response.chart.xLabel}
								yLabel={response.chart.yLabel}
							/>
						{/if}
					</MemoCard>
				{/each}
			</div>
		{/if}
	</main>
	
	<div class="input-area">
		{#if responses.length > 0}
			<SuggestionChips onselect={handleSuggestionSelect} />
		{/if}
		<ChatInput 
			bind:value={query} 
			disabled={loading} 
			onsubmit={handleSubmit}
		/>
	</div>
</div>

<style>
	.page {
		min-height: 100vh;
		max-width: 48rem;
		margin: 0 auto;
		padding: var(--space-6);
		padding-bottom: 10rem;
	}
	
	.header {
		text-align: center;
		padding: var(--space-12) 0 var(--space-8);
	}
	
	.header h1 {
		font-size: var(--text-3xl);
		font-weight: 700;
		letter-spacing: -0.03em;
		margin-bottom: var(--space-1);
	}
	
	.header p {
		color: var(--color-text-tertiary);
		font-size: var(--text-sm);
		margin: 0 auto;
	}
	
	.main {
		flex: 1;
	}
	
	.hero {
		text-align: center;
		padding: var(--space-16) 0;
	}
	
	.hero h2 {
		font-size: var(--text-2xl);
		margin-bottom: var(--space-2);
	}
	
	.hero > p {
		margin: 0 auto var(--space-8);
	}
	
	.hero-suggestions {
		max-width: 32rem;
		margin: 0 auto;
	}
	
	.responses {
		display: flex;
		flex-direction: column;
		gap: var(--space-6);
	}
	
	.input-area {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		padding: var(--space-4) var(--space-6) var(--space-8);
		background: linear-gradient(to top, var(--color-bg) 70%, transparent);
	}
	
	.input-area :global(.suggestions-container) {
		max-width: 48rem;
		margin: 0 auto var(--space-3);
	}
</style>
