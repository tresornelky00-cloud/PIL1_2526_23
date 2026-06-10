// IFRI MentorLink — Main JS
// Mobile sidebar toggle
const sidebar = document.getElementById('sidebar');
if (sidebar) {
  // Auto-close on small screens when link clicked
  document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', () => {
      if (window.innerWidth < 768) sidebar.classList.remove('open');
    });
  });
}
