// Add subtle visual upgrades: hero banner gradients, cards, and CTA glow
(function(){
  function enhance(){
    // hero gradient if header exists
    document.querySelectorAll('header').forEach(h => {
      h.classList.add('bg-gradient-to-r','from-blue-900','to-indigo-800','text-white','shadow');
    });
    // cardify sections
    document.querySelectorAll('section').forEach(s => {
      if(!s.closest('header') && !s.closest('footer')){
        s.classList.add('scroll-mt-24');
      }
    });
    // elevate CTA buttons
    document.querySelectorAll('a.bg-blue-600, a.bg-green-600').forEach(a => {
      a.classList.add('shadow','shadow-blue-200','transition','transform','hover:-translate-y-0.5');
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', enhance); else enhance();
})();
