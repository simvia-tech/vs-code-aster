<script lang="ts">
  import { groupHierarchy } from '../lib/state';
  import Sidebar from './Sidebar.svelte';
  import TopActions from './TopActions.svelte';
  import ZoomWidget from './ZoomWidget.svelte';
  import Popup from './popups/Popup.svelte';
  import HelpPopup from './popups/HelpPopup.svelte';
  import SettingsPopup from './popups/SettingsPopup.svelte';
  import GroupsPopup from './popups/GroupsPopup.svelte';

  type PopupType = 'help' | 'settings' | 'groups' | null;
  let openPopup: PopupType = $state(null);

  let hasData = $derived(Object.keys($groupHierarchy).length > 0);
</script>

{#if hasData}
  <Sidebar onOpenGroups={() => { openPopup = 'groups'; }} />
{/if}

<TopActions
  onOpenSettings={() => { openPopup = 'settings'; }}
  onOpenHelp={() => { openPopup = 'help'; }}
/>

<ZoomWidget />

{#if openPopup}
  <Popup onclose={() => { openPopup = null; }}>
    {#if openPopup === 'help'}
      <HelpPopup onclose={() => { openPopup = null; }} />
    {:else if openPopup === 'settings'}
      <SettingsPopup onclose={() => { openPopup = null; }} />
    {:else if openPopup === 'groups'}
      <GroupsPopup onclose={() => { openPopup = null; }} />
    {/if}
  </Popup>
{/if}
