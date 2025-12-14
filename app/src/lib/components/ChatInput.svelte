<script lang="ts">
	import Icon from '@iconify/svelte';
	
	interface Props {
		value?: string;
		placeholder?: string;
		disabled?: boolean;
		onsubmit?: (query: string) => void;
	}
	
	let { 
		value = $bindable(''), 
		placeholder = 'Ask about NFL stats...',
		disabled = false,
		onsubmit 
	}: Props = $props();
	
	function handleSubmit() {
		if (value.trim() && !disabled) {
			onsubmit?.(value.trim());
		}
	}
	
	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			handleSubmit();
		}
	}
</script>

<div class="chat-input-container">
	<div class="input-wrapper" class:disabled>
		<input
			type="text"
			bind:value
			{placeholder}
			{disabled}
			onkeydown={handleKeydown}
			class="chat-input"
		/>
		<button 
			class="send-button" 
			onclick={handleSubmit}
			disabled={disabled || !value.trim()}
			aria-label="Send message"
		>
			<Icon icon="lucide:arrow-up" width="20" height="20" />
		</button>
	</div>
</div>

<style>
	.chat-input-container {
		position: fixed;
		bottom: 0;
		left: 0;
		right: 0;
		padding: var(--space-4) var(--space-4) var(--space-6);
		background: linear-gradient(to top, var(--color-background) 80%, transparent);
		pointer-events: none;
	}
	
	.input-wrapper {
		max-width: 48rem;
		margin: 0 auto;
		display: flex;
		align-items: center;
		gap: var(--space-2);
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-xl);
		padding: var(--space-2) var(--space-3);
		box-shadow: var(--shadow-lg);
		pointer-events: auto;
		transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
	}
	
	.input-wrapper:focus-within {
		border-color: var(--color-accent);
		box-shadow: var(--shadow-lg), 0 0 0 3px rgba(59, 130, 246, 0.1);
	}
	
	.input-wrapper.disabled {
		opacity: 0.6;
		pointer-events: none;
	}
	
	.chat-input {
		flex: 1;
		border: none;
		background: transparent;
		font-size: var(--text-base);
		color: var(--color-text);
		outline: none;
		padding: var(--space-2);
	}
	
	.chat-input::placeholder {
		color: var(--color-text-subtle);
	}
	
	.send-button {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 2.5rem;
		height: 2.5rem;
		border: none;
		border-radius: var(--radius-full);
		background: var(--color-accent);
		color: white;
		cursor: pointer;
		transition: background-color var(--transition-fast), transform var(--transition-fast);
	}
	
	.send-button:hover:not(:disabled) {
		background: var(--color-accent-hover);
		transform: scale(1.05);
	}
	
	.send-button:disabled {
		background: var(--color-border);
		cursor: not-allowed;
	}
</style>
