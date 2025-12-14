<script lang="ts">
	import ChatInput from '$lib/components/ChatInput.svelte';
	import SuggestionChips from '$lib/components/SuggestionChips.svelte';
	import MemoCard from '$lib/components/MemoCard.svelte';
	import SignupModal from '$lib/components/SignupModal.svelte';
	import TufteDotPlot from '$lib/charts/TufteDotPlot.svelte';
	import Icon from '@iconify/svelte';
	import { SignedIn, SignedOut, SignInButton, UserButton } from 'svelte-clerk';
	import type { AnalyzeResponse } from '$lib/api/client';
	
	// State
	let query = $state('');
	let loading = $state(false);
	let responses = $state<AnalyzeResponse[]>([]);
	let showModal = $state(false);
	let queryCount = $state(0);
	const FREE_QUERY_LIMIT = 20; // Demo mode
	
	// COMPREHENSIVE DEMO DATA - Multiple charts per response
	const DEMO_RESPONSES: Record<string, AnalyzeResponse> = {
		'Compare Patrick Mahomes and Josh Allen EPA per play this season': {
			headline: 'Mahomes vs Allen: A Deep Dive into QB Efficiency',
			summary: `<p>While <strong>Josh Allen</strong> leads overall EPA/play at <span class="positive">+0.31</span>, the comparison with <strong>Patrick Mahomes</strong> (<span class="positive">+0.14</span>) requires context across multiple dimensions.</p>`,
			insights: [
				'Allen leads in raw EPA but Mahomes has better EPA in high-leverage situations',
				'Allen has faced easier defensive schedules on average',
				'Mahomes shows more consistency week-to-week with lower variance'
			],
			charts: [
				{
					type: 'dot',
					title: 'Overall EPA/Play Rankings',
					xLabel: 'Quarterback',
					yLabel: 'EPA/Play',
					data: [
						{ name: 'J. Allen', value: 0.31 },
						{ name: 'L. Jackson', value: 0.29 },
						{ name: 'J. Love', value: 0.24 },
						{ name: 'J. Goff', value: 0.21 },
						{ name: 'B. Purdy', value: 0.19 },
						{ name: 'S. Darnold', value: 0.17 },
						{ name: 'P. Mahomes', value: 0.14 },
						{ name: 'T. Tagovailoa', value: 0.11 }
					]
				},
				{
					type: 'dot',
					title: 'EPA on 3rd Down (High Leverage)',
					xLabel: 'Quarterback',
					yLabel: 'EPA/Play',
					data: [
						{ name: 'P. Mahomes', value: 0.42 },
						{ name: 'L. Jackson', value: 0.38 },
						{ name: 'J. Allen', value: 0.35 },
						{ name: 'J. Goff', value: 0.28 },
						{ name: 'B. Purdy', value: 0.25 },
						{ name: 'S. Darnold', value: 0.19 }
					]
				},
				{
					type: 'dot',
					title: 'Red Zone EPA/Play',
					xLabel: 'Quarterback',
					yLabel: 'EPA/Play',
					data: [
						{ name: 'J. Allen', value: 0.58 },
						{ name: 'P. Mahomes', value: 0.51 },
						{ name: 'L. Jackson', value: 0.48 },
						{ name: 'J. Goff', value: 0.42 },
						{ name: 'B. Purdy', value: 0.35 },
						{ name: 'S. Darnold', value: 0.28 }
					]
				},
				{
					type: 'dot',
					title: 'EPA vs Top-10 Defenses',
					xLabel: 'Quarterback',
					yLabel: 'EPA/Play',
					data: [
						{ name: 'P. Mahomes', value: 0.22 },
						{ name: 'J. Allen', value: 0.18 },
						{ name: 'L. Jackson', value: 0.15 },
						{ name: 'B. Purdy', value: 0.08 },
						{ name: 'J. Goff', value: 0.04 },
						{ name: 'S. Darnold', value: -0.05 }
					]
				}
			]
		},
		'How are the Seahawks doing on 3rd down this season?': {
			headline: 'Seahawks 3rd Down Analysis: Context Matters',
			summary: `<p>Seattle's <span class="positive">43.79%</span> 3rd down rate (16th) tells only part of the story. Breaking down by distance, situation, and trend reveals where improvement is needed.</p>`,
			insights: [
				'Seahawks excel on 3rd-and-short (1-3 yards) but struggle on 3rd-and-long',
				'Home vs away split shows 8% better conversion at home',
				'Recent 4-week trend shows improvement from 38% to 47%'
			],
			charts: [
				{
					type: 'dot',
					title: 'League 3rd Down Conversion Rankings',
					xLabel: 'Team',
					yLabel: '3rd Down %',
					data: [
						{ name: 'GB', value: 0.510 },
						{ name: 'TB', value: 0.509 },
						{ name: 'KC', value: 0.480 },
						{ name: 'SEA', value: 0.438 },
						{ name: 'DET', value: 0.411 },
						{ name: 'NYJ', value: 0.373 },
						{ name: 'TEN', value: 0.311 }
					]
				},
				{
					type: 'dot',
					title: 'Seahawks by Distance to Go',
					xLabel: 'Distance',
					yLabel: 'Conversion %',
					data: [
						{ name: '3rd & 1-2', value: 0.72 },
						{ name: '3rd & 3-4', value: 0.58 },
						{ name: '3rd & 5-6', value: 0.45 },
						{ name: '3rd & 7-9', value: 0.31 },
						{ name: '3rd & 10+', value: 0.18 }
					]
				},
				{
					type: 'dot',
					title: 'Seahawks 3rd Down: Home vs Away',
					xLabel: 'Location',
					yLabel: 'Conversion %',
					data: [
						{ name: 'Home', value: 0.48 },
						{ name: 'Away', value: 0.40 },
						{ name: 'Dome', value: 0.52 },
						{ name: 'Outdoor', value: 0.42 }
					]
				},
				{
					type: 'dot',
					title: '3rd Down Trend (4-Week Rolling)',
					xLabel: 'Weeks',
					yLabel: 'Conversion %',
					data: [
						{ name: 'Wk 1-4', value: 0.38 },
						{ name: 'Wk 5-8', value: 0.42 },
						{ name: 'Wk 9-12', value: 0.45 },
						{ name: 'Wk 13-14', value: 0.47 }
					]
				}
			]
		},
		'Which teams have the best red zone touchdown percentage?': {
			headline: 'Red Zone Efficiency: Offense, Defense, and Context',
			summary: `<p><strong>Baltimore Ravens</strong> lead at <span class="positive">77.78%</span> red zone TD rate, but analyzing both offense, defense, and situational context reveals the full picture.</p>`,
			insights: [
				'Ravens dominant offense but Denver has best red zone defense at 40% opponent TD rate',
				'Running-heavy teams (BAL, DET) outperform passing-focused teams in red zone',
				'Goal-to-go situations show even wider efficiency gaps between top and bottom'
			],
			charts: [
				{
					type: 'dot',
					title: 'Offensive Red Zone TD%',
					xLabel: 'Team',
					yLabel: 'TD %',
					data: [
						{ name: 'BAL', value: 0.778 },
						{ name: 'CIN', value: 0.697 },
						{ name: 'TB', value: 0.684 },
						{ name: 'DET', value: 0.683 },
						{ name: 'GB', value: 0.681 },
						{ name: 'KC', value: 0.620 },
						{ name: 'SEA', value: 0.550 },
						{ name: 'NYG', value: 0.480 }
					]
				},
				{
					type: 'dot',
					title: 'Defensive Red Zone TD% Allowed',
					xLabel: 'Team',
					yLabel: 'Opp TD % (lower = better)',
					data: [
						{ name: 'DEN', value: 0.40 },
						{ name: 'BAL', value: 0.45 },
						{ name: 'KC', value: 0.48 },
						{ name: 'SF', value: 0.52 },
						{ name: 'DET', value: 0.55 },
						{ name: 'PHI', value: 0.58 },
						{ name: 'NYG', value: 0.72 }
					]
				},
				{
					type: 'dot',
					title: 'Goal-to-Go TD% (Inside 5 Yards)',
					xLabel: 'Team',
					yLabel: 'TD %',
					data: [
						{ name: 'BAL', value: 0.92 },
						{ name: 'DET', value: 0.88 },
						{ name: 'KC', value: 0.85 },
						{ name: 'GB', value: 0.82 },
						{ name: 'TB', value: 0.78 },
						{ name: 'SEA', value: 0.68 }
					]
				},
				{
					type: 'dot',
					title: 'Red Zone Attempts per Game',
					xLabel: 'Team',
					yLabel: 'Attempts/Game',
					data: [
						{ name: 'DET', value: 4.8 },
						{ name: 'BAL', value: 4.5 },
						{ name: 'KC', value: 4.2 },
						{ name: 'TB', value: 3.9 },
						{ name: 'GB', value: 3.7 },
						{ name: 'SEA', value: 3.4 }
					]
				}
			]
		}
	};
	
	async function handleSubmit(q: string) {
		if (!q.trim()) return;
		
		// Check if user can query (demo mode with 20 free queries)
		if (queryCount >= FREE_QUERY_LIMIT) {
			showModal = true;
			return;
		}
		
		loading = true;
		await new Promise(resolve => setTimeout(resolve, 1200));
		
		// Increment query count
		queryCount++;
		
		const demoResponse = DEMO_RESPONSES[q];
		if (demoResponse) {
			responses = [demoResponse, ...responses];
		} else {
			responses = [{
				headline: 'Query Received',
				summary: `<p>Analysis for "<em>${q}</em>" requires backend connection. Try the demo queries to see comprehensive multi-chart analysis!</p>`,
			}, ...responses];
		}
		
		query = '';
		loading = false;
		
		// Show modal after query completes if limit reached
		if (queryCount >= FREE_QUERY_LIMIT) {
			setTimeout(() => { showModal = true; }, 500);
		}
	}
	
	function handleSuggestionSelect(q: string) {
		query = q;
		handleSubmit(q);
	}
</script>

<div class="page">
	<header class="header">
		<div class="header-left">
			<div class="logo">
				<div class="logo-icon">
					<Icon icon="lucide:grid-3x3" width="24" height="24" />
				</div>
				<h1>Gridiron</h1>
			</div>
		</div>
		<div class="header-right">
			<SignedOut>
				<SignInButton mode="modal">
					<button class="sign-in-btn">Sign In</button>
				</SignInButton>
			</SignedOut>
			<SignedIn>
				<UserButton />
			</SignedIn>
		</div>
	</header>
	
	<main class="main">
		{#if responses.length === 0 && !loading}
			<div class="hero">
				<div class="hero-content">
					<h2>Ask anything about the NFL</h2>
					<p class="hero-description">
						Get comprehensive insights with multiple visualizations showing different contexts and perspectives.
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
						<!-- Key Insights -->
						{#if response.insights && response.insights.length > 0}
							<div class="insights">
								<h4 class="insights-title">
									<Icon icon="lucide:lightbulb" width="16" height="16" />
									Key Insights
								</h4>
								<ul class="insights-list">
									{#each response.insights as insight}
										<li>{insight}</li>
									{/each}
								</ul>
							</div>
						{/if}
						
						<!-- Multiple Charts -->
						{#if response.charts && response.charts.length > 0}
							<div class="charts-grid">
								{#each response.charts as chart}
									<div class="chart-section">
										<h4 class="chart-title">{chart.title}</h4>
										<TufteDotPlot 
											data={chart.data} 
											xLabel={chart.xLabel}
											yLabel={chart.yLabel}
										/>
									</div>
								{/each}
							</div>
						{:else if response.chart}
							<!-- Legacy single chart support -->
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
		<SignedOut>
			{#if FREE_QUERY_LIMIT - queryCount <= 5 && FREE_QUERY_LIMIT - queryCount > 0}
				<div class="query-counter">
					<Icon icon="lucide:sparkles" width="14" height="14" />
					<span>{FREE_QUERY_LIMIT - queryCount} free queries remaining</span>
				</div>
			{/if}
		</SignedOut>
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
	<SignupModal onclose={() => { showModal = false; }} />
{/if}

<style>
	.page {
		min-height: 100vh;
		padding: var(--space-4) var(--space-8) 10rem;
	}
	
	.header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: var(--space-4) 0;
	}

	.header-left {
		display: flex;
		align-items: center;
	}

	.header-right {
		display: flex;
		align-items: center;
	}
	
	.logo {
		display: flex;
		align-items: center;
		gap: var(--space-2);
	}

	.logo-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2rem;
		height: 2rem;
		background: var(--accent);
		color: white;
		border-radius: var(--radius-md);
	}
	
	.header h1 {
		font-size: var(--text-xl);
		font-weight: 700;
		letter-spacing: -0.03em;
	}

	.sign-in-btn {
		padding: var(--space-2) var(--space-4);
		background: var(--accent);
		color: white;
		border: none;
		border-radius: var(--radius-md);
		font-size: var(--text-sm);
		font-weight: 500;
		cursor: pointer;
		transition: background var(--transition-fast);
	}

	.sign-in-btn:hover {
		background: var(--accent-soft);
	}
	
	.main {
		flex: 1;
	}
	
	.hero {
		text-align: center;
		padding: var(--space-8) 0;
		animation: fadeInUp 0.6s ease-out;
	}

	.hero-content {
		margin-bottom: var(--space-6);
	}
	
	.hero h2 {
		font-size: var(--text-xl);
		font-weight: 600;
		margin-bottom: var(--space-2);
		color: var(--color-text);
	}
	
	.hero-description {
		max-width: 28rem;
		margin: 0 auto;
		color: var(--color-text-secondary);
		font-size: var(--text-sm);
		line-height: 1.5;
	}
	
	.hero-chips {
		max-width: 40rem;
		margin: 0 auto;
	}
	
	.responses {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
	}

	/* Insights Section - Compact */
	.insights {
		margin-bottom: var(--space-4);
		padding: var(--space-3);
		background: var(--color-bg-subtle);
		border-radius: var(--radius-md);
		border-left: 2px solid var(--accent);
	}

	.insights-title {
		display: flex;
		align-items: center;
		gap: var(--space-2);
		font-size: var(--text-xs);
		font-weight: 600;
		color: var(--accent);
		margin-bottom: var(--space-2);
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.insights-list {
		margin: 0;
		padding-left: var(--space-4);
		font-size: var(--text-sm);
		color: var(--color-text-secondary);
	}

	.insights-list li {
		margin-bottom: var(--space-1);
		line-height: 1.4;
	}

	.insights-list li:last-child {
		margin-bottom: 0;
	}

	/* Multi-Chart Grid - Full Width */
	.charts-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: var(--space-4);
	}

	@media (max-width: 1200px) {
		.charts-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	@media (max-width: 640px) {
		.charts-grid {
			grid-template-columns: 1fr;
		}
	}

	.chart-section {
		padding: var(--space-3);
		background: var(--color-surface);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
	}

	.chart-title {
		font-size: var(--text-xs);
		font-weight: 600;
		color: var(--color-text);
		margin-bottom: var(--space-2);
		padding-bottom: var(--space-1);
		border-bottom: 1px solid var(--color-border);
	}
	
	.input-area {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		padding: var(--space-2) var(--space-8) var(--space-4);
		background: linear-gradient(to top, var(--color-bg) 80%, transparent);
	}

	.query-counter {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--space-2);
		margin-bottom: var(--space-2);
		font-size: var(--text-xs);
		color: var(--accent);
	}

	.input-suggestions {
		max-width: 48rem;
		margin: 0 auto var(--space-2);
	}

	@keyframes fadeIn {
		from { opacity: 0; }
		to { opacity: 1; }
	}

	@keyframes fadeInUp {
		from { opacity: 0; transform: translateY(10px); }
		to { opacity: 1; transform: translateY(0); }
	}
</style>
