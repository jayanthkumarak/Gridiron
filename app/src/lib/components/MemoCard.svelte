<script lang="ts">
	import type { Snippet } from 'svelte';
	
	interface Props {
		headline: string;
		summary?: string;
		loading?: boolean;
		children?: Snippet;
	}
	
	let { headline, summary, loading = false, children }: Props = $props();
</script>

<article class="memo-card" class:loading>
	{#if loading}
		<div class="loading-state">
			<div class="loading-shimmer headline-shimmer"></div>
			<div class="loading-shimmer summary-shimmer"></div>
			<div class="loading-shimmer summary-shimmer short"></div>
			<div class="loading-shimmer chart-shimmer"></div>
		</div>
	{:else}
		<header class="memo-header">
			<h2 class="memo-headline">{headline}</h2>
		</header>
		
		{#if summary}
			<div class="memo-summary">
				{@html summary}
			</div>
		{/if}
		
		{#if children}
			<div class="memo-content">
				{@render children()}
			</div>
		{/if}
	{/if}
</article>

<style>
	.memo-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: var(--space-6);
		margin-bottom: var(--space-4);
		box-shadow: var(--shadow-sm);
	}
	
	.memo-header {
		margin-bottom: var(--space-4);
		padding-bottom: var(--space-4);
		border-bottom: 1px solid var(--color-border);
	}
	
	.memo-headline {
		font-size: var(--text-xl);
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.3;
		margin: 0;
	}
	
	.memo-summary {
		font-size: var(--text-base);
		color: var(--color-text);
		line-height: 1.7;
		margin-bottom: var(--space-6);
	}
	
	.memo-summary :global(p) {
		margin-bottom: var(--space-3);
	}
	
	.memo-summary :global(strong) {
		font-weight: 600;
		color: var(--color-text);
	}
	
	.memo-summary :global(.positive) {
		color: var(--color-positive);
		font-weight: 600;
	}
	
	.memo-summary :global(.negative) {
		color: var(--color-negative);
		font-weight: 600;
	}
	
	.memo-content {
		margin-top: var(--space-4);
	}
	
	/* Loading State */
	.loading-state {
		display: flex;
		flex-direction: column;
		gap: var(--space-3);
	}
	
	.loading-shimmer {
		background: linear-gradient(
			90deg,
			var(--color-border) 25%,
			var(--slate-200) 50%,
			var(--color-border) 75%
		);
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
		border-radius: var(--radius-sm);
	}
	
	.headline-shimmer {
		height: 1.75rem;
		width: 70%;
	}
	
	.summary-shimmer {
		height: 1rem;
		width: 100%;
	}
	
	.summary-shimmer.short {
		width: 60%;
	}
	
	.chart-shimmer {
		height: 12rem;
		width: 100%;
		margin-top: var(--space-4);
	}
	
	@keyframes shimmer {
		0% { background-position: 200% 0; }
		100% { background-position: -200% 0; }
	}
	
	@media (prefers-color-scheme: dark) {
		.loading-shimmer {
			background: linear-gradient(
				90deg,
				var(--slate-800) 25%,
				var(--slate-700) 50%,
				var(--slate-800) 75%
			);
			background-size: 200% 100%;
		}
	}
</style>
