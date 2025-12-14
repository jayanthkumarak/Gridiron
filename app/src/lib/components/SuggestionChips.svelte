<script lang="ts">
	interface Suggestion {
		id: string;
		label: string;
		query: string;
	}
	
	interface Props {
		suggestions?: Suggestion[];
		onselect?: (query: string) => void;
	}
	
	const defaultSuggestions: Suggestion[] = [
		{
			id: '1',
			label: 'Mahomes vs Allen EPA/play',
			query: 'Compare Patrick Mahomes and Josh Allen EPA per play this season'
		},
		{
			id: '2',
			label: 'Seahawks 3rd Down',
			query: 'How are the Seahawks doing on 3rd down this season?'
		},
		{
			id: '3',
			label: 'Best Red Zone Offenses',
			query: 'Which teams have the best red zone touchdown percentage?'
		}
	];
	
	let { 
		suggestions = defaultSuggestions,
		onselect 
	}: Props = $props();
</script>

<div class="suggestions-container">
	<div class="suggestions-label">Try asking</div>
	<div class="suggestions-chips">
		{#each suggestions as suggestion (suggestion.id)}
			<button 
				class="chip"
				onclick={() => onselect?.(suggestion.query)}
			>
				{suggestion.label}
			</button>
		{/each}
	</div>
</div>

<style>
	.suggestions-container {
		display: flex;
		flex-direction: column;
		gap: var(--space-2);
		margin-bottom: var(--space-4);
	}
	
	.suggestions-label {
		font-size: var(--text-sm);
		color: var(--color-text-muted);
		font-weight: 500;
	}
	
	.suggestions-chips {
		display: flex;
		flex-wrap: wrap;
		gap: var(--space-2);
	}
	
	.chip {
		display: inline-flex;
		align-items: center;
		padding: var(--space-2) var(--space-4);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-full);
		font-size: var(--text-sm);
		color: var(--color-text);
		cursor: pointer;
		transition: all var(--transition-fast);
		white-space: nowrap;
	}
	
	.chip:hover {
		background: var(--slate-100);
		border-color: var(--color-accent);
		color: var(--color-accent);
	}
	
	@media (prefers-color-scheme: dark) {
		.chip:hover {
			background: var(--slate-800);
		}
	}
</style>
