// Scroll animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
        }
    });
}, observerOptions);

document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));

// Navbar scroll effect
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
    if (window.pageYOffset > 100) {
        navbar.style.boxShadow = '0 4px 20px rgba(0,0,0,0.08)';
    } else {
        navbar.style.boxShadow = 'none';
    }
});

// FAQ Accordion
document.querySelectorAll('.faq-question').forEach(question => {
    question.addEventListener('click', () => {
        const item = question.parentElement;
        const isActive = item.classList.contains('active');

        // Close all
        document.querySelectorAll('.faq-item').forEach(faq => {
            faq.classList.remove('active');
        });

        // Open clicked if it wasn't active
        if (!isActive) {
            item.classList.add('active');
        }
    });
});
