<script lang="ts">
	import type { Snippet } from 'svelte';
	import Icon from '@iconify/svelte';
	
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
			<div class="loading-header">
				<div class="loading-icon"></div>
				<div class="loading-shimmer headline-shimmer"></div>
			</div>
			<div class="loading-body">
				<div class="loading-shimmer line-shimmer"></div>
				<div class="loading-shimmer line-shimmer w-90"></div>
				<div class="loading-shimmer line-shimmer w-75"></div>
			</div>
			<div class="loading-shimmer chart-shimmer"></div>
		</div>
	{:else}
		<header class="memo-header">
			<div class="memo-icon">
				<Icon icon="lucide:file-text" width="20" height="20" />
			</div>
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
		border-radius: var(--radius-xl);
		padding: var(--space-6);
		box-shadow: var(--shadow-md);
		animation: cardEnter 0.4s ease-out;
	}
	
	@keyframes cardEnter {
		from {
			opacity: 0;
			transform: translateY(16px) scale(0.98);
		}
		to {
			opacity: 1;
			transform: translateY(0) scale(1);
		}
	}
	
	.memo-header {
		display: flex;
		align-items: flex-start;
		gap: var(--space-3);
		margin-bottom: var(--space-4);
		padding-bottom: var(--space-4);
		border-bottom: 1px solid var(--color-border);
	}

	.memo-icon {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2rem;
		height: 2rem;
		background: var(--accent-glow);
		color: var(--accent);
		border-radius: var(--radius-md);
		flex-shrink: 0;
	}
	
	.memo-headline {
		font-size: var(--text-lg);
		font-weight: 600;
		color: var(--color-text);
		line-height: 1.4;
		margin: 0;
	}
	
	.memo-summary {
		font-size: var(--text-base);
		color: var(--color-text-secondary);
		line-height: 1.7;
	}
	
	.memo-summary :global(p) {
		margin-bottom: var(--space-3);
	}

	.memo-summary :global(p:last-child) {
		margin-bottom: 0;
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

	.memo-summary :global(ul) {
		margin: var(--space-2) 0;
		padding-left: var(--space-5);
	}

	.memo-summary :global(li) {
		margin-bottom: var(--space-1);
	}
	
	.memo-content {
		margin-top: var(--space-5);
		padding-top: var(--space-4);
		border-top: 1px solid var(--color-border);
	}
	
	/* Loading State */
	.loading-state {
		display: flex;
		flex-direction: column;
		gap: var(--space-4);
	}

	.loading-header {
		display: flex;
		align-items: center;
		gap: var(--space-3);
	}

	.loading-icon {
		width: 2rem;
		height: 2rem;
		background: var(--color-border);
		border-radius: var(--radius-md);
		animation: pulse 1.5s ease-in-out infinite;
	}

	.loading-body {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
	}
	
	.loading-shimmer {
		background: linear-gradient(
			90deg,
			var(--color-border) 25%,
			var(--color-bg-subtle) 50%,
			var(--color-border) 75%
		);
		background-size: 200% 100%;
		animation: shimmer 1.5s infinite;
		border-radius: var(--radius-sm);
	}
	
	.headline-shimmer {
		height: 1.5rem;
		flex: 1;
		max-width: 60%;
	}
	
	.line-shimmer {
		height: 1rem;
		width: 100%;
	}

	.line-shimmer.w-90 { width: 90%; }
	.line-shimmer.w-75 { width: 75%; }
	
	.chart-shimmer {
		height: 14rem;
		width: 100%;
		border-radius: var(--radius-lg);
	}
	
	@keyframes shimmer {
		0% { background-position: 200% 0; }
		100% { background-position: -200% 0; }
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}
</style>
