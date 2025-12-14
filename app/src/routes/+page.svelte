<script lang="ts">
	import ChatInput from '$lib/components/ChatInput.svelte';
	import SuggestionChips from '$lib/components/SuggestionChips.svelte';
	import MemoCard from '$lib/components/MemoCard.svelte';
	import SignupModal from '$lib/components/SignupModal.svelte';
	import TufteDotPlot from '$lib/charts/TufteDotPlot.svelte';
	import Icon from '@iconify/svelte';
	import { authStore } from '$lib/stores/authStore';
	import type { AnalyzeResponse } from '$lib/api/client';
	
	// State
	let query = $state('');
	let loading = $state(false);
	let responses = $state<AnalyzeResponse[]>([]);
	
	// Subscribe to auth store
	let showModal = $derived($authStore.showSignupModal);
	let isAuthenticated = $derived($authStore.isAuthenticated);
	let remainingQueries = $derived(authStore.remainingQueries());
	
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
		
		// Check if user can query
		if (!authStore.canQuery()) {
			authStore.showModal();
			return;
		}
		
		loading = true;
		await new Promise(resolve => setTimeout(resolve, 800));
		
		// Record the query and check if we should show gate
		const shouldShowGate = authStore.recordQuery();
		
		const demoResponse = DEMO_RESPONSES[q];
		if (demoResponse) {
			responses = [demoResponse, ...responses];
		} else {
			responses = [{
				headline: 'Query Received',
				summary: `<p>Analysis for "<em>${q}</em>" requires backend connection. Try the demo queries!</p>`,
			}, ...responses];
		}
		
		query = '';
		loading = false;
		
		// Show modal after query completes if limit reached
		if (shouldShowGate) {
			setTimeout(() => authStore.showModal(), 500);
		}
	}
	
	function handleSuggestionSelect(q: string) {
		query = q;
		handleSubmit(q);
	}
</script>

<div class="page">
	<header class="header">
		<div class="logo">
			<div class="logo-icon">
				<Icon icon="lucide:grid-3x3" width="24" height="24" />
			</div>
			<h1>Gridiron</h1>
		</div>
		<p class="tagline">NFL Analytics powered by play-by-play data</p>
	</header>
	
	<main class="main">
		{#if responses.length === 0 && !loading}
			<div class="hero">
				<div class="hero-content">
					<h2>Ask anything about the NFL</h2>
					<p class="hero-description">
						Get instant insights from real-time EPA metrics, situational analysis, 
						and advanced player stats.
					</p>
				</div>
				<div class="hero-chips">
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
		{#if !isAuthenticated && remainingQueries <= 3 && remainingQueries > 0}
			<div class="query-counter">
				<Icon icon="lucide:sparkles" width="14" height="14" />
				<span>{remainingQueries} free {remainingQueries === 1 ? 'query' : 'queries'} remaining</span>
			</div>
		{/if}
		{#if responses.length > 0}
			<div class="input-suggestions">
				<SuggestionChips onselect={handleSuggestionSelect} />
			</div>
		{/if}
		<ChatInput 
			bind:value={query} 
			disabled={loading} 
			onsubmit={handleSubmit}
		/>
	</div>
</div>

{#if showModal}
	<SignupModal onclose={() => authStore.hideModal()} />
{/if}

<style>
	.page {
		min-height: 100vh;
		max-width: 52rem;
		margin: 0 auto;
		padding: var(--space-6) var(--space-6) 12rem;
	}
	
	.header {
		text-align: center;
		padding: var(--space-10) 0 var(--space-6);
		animation: fadeIn 0.5s ease-out;
	}
	
	.logo {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-3);
		margin-bottom: var(--space-2);
	}

	.logo-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2.5rem;
		height: 2.5rem;
		background: var(--accent);
		color: white;
		border-radius: var(--radius-lg);
	}
	
	.header h1 {
		font-size: var(--text-3xl);
		font-weight: 700;
		letter-spacing: -0.03em;
		background: linear-gradient(135deg, var(--color-text) 0%, var(--gray-600) 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}
	
	.tagline {
		color: var(--color-text-tertiary);
		font-size: var(--text-sm);
		margin: 0;
	}
	
	.main {
		flex: 1;
	}
	
	.hero {
		text-align: center;
		padding: var(--space-12) 0 var(--space-8);
		animation: fadeInUp 0.6s ease-out;
	}

	.hero-content {
		margin-bottom: var(--space-10);
	}
	
	.hero h2 {
		font-size: var(--text-2xl);
		font-weight: 600;
		margin-bottom: var(--space-3);
		color: var(--color-text);
	}
	
	.hero-description {
		max-width: 28rem;
		margin: 0 auto;
		color: var(--color-text-secondary);
		line-height: 1.6;
	}
	
	.hero-chips {
		max-width: 36rem;
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
		padding: var(--space-3) var(--space-6) var(--space-6);
		background: linear-gradient(to top, var(--color-bg) 75%, transparent);
	}

	.query-counter {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-2);
		margin-bottom: var(--space-3);
		font-size: var(--text-xs);
		color: var(--accent);
		animation: fadeIn 0.3s ease-out;
	}

	.input-suggestions {
		max-width: 52rem;
		margin: 0 auto var(--space-3);
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	@keyframes fadeInUp {
		from { opacity: 0; transform: translateY(20px); }
		to { opacity: 1; transform: translateY(0); }
	}
</style>
