<script lang="ts">
  interface Props {
    simviaLogoUrl: string;
    simviaLogoDarkUrl: string;
    asterLogoUrl: string;
    asterLogoDarkUrl: string;
  }
  let { simviaLogoUrl, simviaLogoDarkUrl, asterLogoUrl, asterLogoDarkUrl }: Props = $props();
</script>

<header class="flex items-center justify-between gap-4 mb-6">
  <h1 class="text-xl font-semibold text-ui-text-primary tracking-tight">Export File Creation</h1>
  <div class="flex items-center gap-4 shrink-0">
    {#if simviaLogoUrl}
      <img src={simviaLogoUrl} alt="Simvia" class="logo-light h-10 w-auto" />
    {/if}
    {#if simviaLogoDarkUrl}
      <img src={simviaLogoDarkUrl} alt="Simvia" class="logo-dark h-10 w-auto" />
    {/if}
    {#if asterLogoUrl}
      <img src={asterLogoUrl} alt="code_aster" class="logo-light h-6 w-auto" />
    {/if}
    {#if asterLogoDarkUrl}
      <img src={asterLogoDarkUrl} alt="code_aster" class="logo-dark h-6 w-auto" />
    {/if}
  </div>
</header>

<style>
  .logo-dark {
    display: none;
  }
  :global(body.vscode-dark) .logo-light,
  :global(body.vscode-high-contrast:not(.vscode-high-contrast-light)) .logo-light {
    display: none;
  }
  :global(body.vscode-dark) .logo-dark,
  :global(body.vscode-high-contrast:not(.vscode-high-contrast-light)) .logo-dark {
    display: inline-block;
  }
</style>
