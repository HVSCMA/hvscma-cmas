// Lightweight client-side index for listings navigation
(function(){
  const NAV_ID = 'hv-listings-nav';
  const API_URL = '/data/listings.json';

  function createNav(items){
    const wrapper = document.createElement('div');
    wrapper.id = NAV_ID;
    wrapper.className = 'sticky top-0 z-40 bg-white/90 backdrop-blur border-b';
    wrapper.innerHTML = `
      <div class="max-w-6xl mx-auto px-4 py-3 flex flex-wrap items-center gap-3">
        <a class="text-blue-800 font-semibold" href="/">HVSCMA</a>
        <nav class="flex-1 flex flex-wrap gap-2 text-sm" id="hv-listings-links"></nav>
        <div class="ml-auto flex gap-2">
          <input id="hv-listings-search" class="border rounded px-2 py-1 text-sm" placeholder="Search address / town"/>
        </div>
      </div>`;

    const links = wrapper.querySelector('#hv-listings-links');
    function render(filter=''){
      links.innerHTML = '';
      const q = filter.trim().toLowerCase();
      items.filter(it => {
        const hay = `${it.address} ${it.city} ${it.state} ${it.zip}`.toLowerCase();
        return !q || hay.includes(q);
      }).slice(0,50).forEach(it => {
        const a = document.createElement('a');
        a.href = it.path;
        a.className = 'px-2 py-1 rounded hover:bg-blue-50 text-blue-700';
        a.textContent = it.address;
        links.appendChild(a);
      });
    }

    const input = wrapper.querySelector('#hv-listings-search');
    input.addEventListener('input', () => render(input.value));
    render();
    return wrapper;
  }

  async function main(){
    try {
      const res = await fetch(API_URL, {cache:'no-store'});
      if(!res.ok) throw new Error('Failed to load listings index');
      const items = await res.json();
      const nav = createNav(items);
      document.body.prepend(nav);
    } catch(e){
      console.warn('Listings nav init failed:', e);
    }
  }
  if(document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', main);
  else main();
})();
