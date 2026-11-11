// Sticky header shadow on scroll
const header = document.getElementById('site-header');
const onScroll = () => {
  if (window.scrollY > 10) header.classList.add('scrolled');
  else header.classList.remove('scrolled');
};
window.addEventListener('scroll', onScroll);
onScroll();

// Mobile menu toggle
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobile-menu');
hamburger.addEventListener('click', () => {
  mobileMenu.classList.toggle('open');
});
mobileMenu.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => mobileMenu.classList.remove('open'));
});

// Scroll reveal
const revealEls = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
revealEls.forEach(el => observer.observe(el));

// Appointment form: builds a mailto: to the practice's real inbox instead of
// posting anywhere. No network request, no third-party account involved.
const contactForm = document.getElementById('contact-form');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const fname = contactForm.querySelector('#fname').value.trim();
    const lname = contactForm.querySelector('#lname').value.trim();
    const email = contactForm.querySelector('#email').value.trim();
    const message = contactForm.querySelector('#message').value.trim();

    const subject = `New website appointment request from ${fname} ${lname}`.trim();
    const body = `Name: ${fname} ${lname}\nEmail: ${email}\n\n${message}`;

    window.location.href = `mailto:dentistrybliss6332@outlook.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
  });
}
