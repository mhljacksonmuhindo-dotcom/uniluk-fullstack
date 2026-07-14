document.addEventListener("DOMContentLoaded", () => {
  const header = document.getElementById("site-header");
  const burger = document.getElementById("burger");
  const mobileMenu = document.querySelector(".mobile-menu");
  const backToTop = document.createElement("a");
  
  const dateInput=document.getElementById('date_naissance');
   
  if (dateInput){
  const aujourdhui = new Date();
  const annee= aujourdhui.getFullYear();
  const mois = String(aujourdhui.getMonth()+ 1).padStart(2,'0');
  const jour = String(aujourdhui.getDate()).padStart(2,'0');
  const dateMax = `${annee}-${mois}-${jour}`;
  dateInput.max= dateMax;
  }

  const syncBurgerIcon = (isOpen) => {
    if (!burger) return;

    const icon = burger.querySelector("i");
    if (!icon) return;

    icon.className = isOpen ? "fa-solid fa-xmark" : "fa-solid fa-bars";
  };

  if (burger && header && mobileMenu && document.body) {
    backToTop.href = "#";
    backToTop.className = "back-to-top";
    backToTop.innerHTML = "&uarr;";
    document.body.appendChild(backToTop);

    syncBurgerIcon(mobileMenu.classList.contains("open"));

    burger.addEventListener("click", () => {
      mobileMenu.classList.toggle("open");
      syncBurgerIcon(mobileMenu.classList.contains("open"));
    });

    window.addEventListener("scroll", () => {
      header.classList.toggle("scrolled", window.scrollY > 60);
      backToTop.classList.toggle("show", window.scrollY > 420);
    });

    backToTop.addEventListener("click", (event) => {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") {
        mobileMenu.classList.remove("open");
        syncBurgerIcon(false);
      }
    });

    mobileMenu.addEventListener("click", (e) => {
      const isBackdrop = e.target === mobileMenu;
      if (isBackdrop) {
        mobileMenu.classList.remove("open");
        syncBurgerIcon(false);
      }
    });
  }

  if (burger && !mobileMenu) {
    console.warn("#burger trouvé mais .mobile-menu absent sur cette page.");
  }

  const testimonialTrack = document.querySelector(".testimonial-track");

  if (testimonialTrack) {
    const slides = Array.from(testimonialTrack.children);
    if (slides.length > 1) {
      let index = 0;
      setInterval(() => {
        index = (index + 1) % slides.length;
        testimonialTrack.style.transform = `translateX(-${index * 100}%)`;
      }, 7000);
    }
  }

  document.querySelectorAll("img").forEach((image) => {
    if (image.complete && image.naturalWidth === 0) {
      image.classList.add("is-missing");
    }

    image.addEventListener("error", () => {
      image.classList.add("is-missing");
    });
  });

  const setupSlider = (
    rootSelector,
    slideSelector,
    prevSelector,
    nextSelector,
    interval = 6500,
  ) => {
    const root = document.querySelector(rootSelector);
    if (!root) return;

    const slides = Array.from(root.querySelectorAll(slideSelector));
    const prev = root.querySelector(prevSelector);
    const next = root.querySelector(nextSelector);
    const track = root.querySelector(".entity-track");

    if (slides.length <= 1) return;

    let index = 0;
    let timer;

    const show = (nextIndex) => {
      index = (nextIndex + slides.length) % slides.length;

      if (track) {
        track.style.transform = `translateX(-${index * 100}%)`;
      } else {
        slides.forEach((slide, slideIndex) => {
          slide.classList.toggle("active", slideIndex === index);
        });
      }
    };

    const restart = () => {
      clearInterval(timer);
      timer = setInterval(() => show(index + 1), interval);
    };

    prev?.addEventListener("click", () => {
      show(index - 1);
      restart();
    });

    next?.addEventListener("click", () => {
      show(index + 1);
      restart();
    });

    show(0);
    restart();
  };

  setupSlider(
    ".hero",
    ".hero-slide",
    ".hero-control.prev",
    ".hero-control.next",
  );
  setupSlider(
    ".entity-slider",
    ".entity-slide",
    ".entity-control.prev",
    ".entity-control.next",
    7200,
  );
});

function closeMobileMenu() {
  const menu = document.querySelector(".mobile-menu");
  if (menu) menu.classList.remove("open");
}

function toggleMobileDropdown(button) {
  const dropdown = button.nextElementSibling;
  if (!dropdown) return;

  const isGrid = dropdown.style.display === "grid";
  dropdown.style.display = isGrid ? "none" : "grid";
}
