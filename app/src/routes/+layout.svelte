<script lang="ts">
	import '../app.css';
	import { ClerkProvider } from 'svelte-clerk';
	
	interface Props {
		children: import('svelte').Snippet;
	}
	
	let { children }: Props = $props();
</script>

<ClerkProvider>
	<div class="app-container">
		{@render children()}
	</div>
</ClerkProvider>

<style>
	.app-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}
</style>
