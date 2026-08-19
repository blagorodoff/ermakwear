(function () {
  var burger = document.querySelector(".hg-header__burger");
  var mobile = document.querySelector(".hg-header__mobile");
  if (!burger || !mobile) return;

  function close() {
    burger.classList.remove("is-active");
    burger.setAttribute("aria-expanded", "false");
    mobile.classList.remove("is-open");
    mobile.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  function open() {
    burger.classList.add("is-active");
    burger.setAttribute("aria-expanded", "true");
    mobile.classList.add("is-open");
    mobile.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
  }

  burger.addEventListener("click", function () {
    if (mobile.classList.contains("is-open")) {
      close();
    } else {
      open();
    }
  });

  mobile.querySelectorAll("a").forEach(function (link) {
    link.addEventListener("click", close);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && mobile.classList.contains("is-open")) {
      close();
    }
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth > 768 && mobile.classList.contains("is-open")) {
      close();
    }
  });
})();

(function () {
  const video = document.querySelector(".kb-banner__video");
  if (!video) return;
  video.muted = true;
  const tryPlay = () => {
    const p = video.play();
    if (p && typeof p.catch === "function") p.catch(() => {});
  };
  if (video.readyState >= 2) {
    tryPlay();
  } else {
    video.addEventListener("canplay", tryPlay, { once: true });
  }
})();

(function () {
  "use strict";

  var root = document.getElementById("ecCatalog");
  var collectionsEl = document.getElementById("ecCollections");
  var filterTrack = document.getElementById("ecFilterTrack");

  var backdrop = document.getElementById("ecModal");
  var modalClose = document.getElementById("ecModalClose");
  var modalImg = document.getElementById("ecModalImg");
  var modalBadge = document.getElementById("ecModalBadge");
  var modalCollection = document.getElementById("ecModalCollection");
  var modalName = document.getElementById("ecModalName");
  var modalPriceVal = document.getElementById("ecModalPriceVal");
  var modalBuy = document.getElementById("ecModalBuy");
  var modalBuyLbl = document.getElementById("ecModalBuyLabel");
  var modalPrev = document.getElementById("ecModalPrev");
  var modalNext = document.getElementById("ecModalNext");
  var modalDots = document.getElementById("ecModalDots");

  if (!root || !collectionsEl || !filterTrack) return;

  var activeFilter = "all";
  var currentProduct = null;
  var currentImageIndex = 0;
  var currentImages = [];

  // Функция установки фильтра
  function setFilter(filterId) {
    activeFilter = filterId;
    var btns = filterTrack.querySelectorAll(".ec-filter__btn");
    btns.forEach(function (btn) {
      var active = btn.getAttribute("data-filter") === filterId;
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
    var sections = collectionsEl.querySelectorAll(".ec-collection");
    sections.forEach(function (section) {
      var cid = section.getAttribute("data-collection-id");
      var show = filterId === "all" || cid === filterId;
      if (show) {
        section.classList.remove("is-hidden");
        section.classList.remove("is-animating-in");
        void section.offsetWidth;
        section.classList.add("is-animating-in");
      } else {
        section.classList.add("is-hidden");
        section.classList.remove("is-animating-in");
      }
    });
  }

  // Обработка кликов по фильтрам
  filterTrack.addEventListener("click", function (e) {
    var btn = e.target.closest(".ec-filter__btn");
    if (!btn) return;
    var filterId = btn.getAttribute("data-filter");
    if (filterId && filterId !== activeFilter) setFilter(filterId);
  });

  // Функция форматирования цены
  function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, "\u00a0");
  }

  function updateModalImage() {
    if (currentImages.length > 0) {
      modalImg.src =
        "/static/uploads/products/" + currentImages[currentImageIndex];
    } else {
      modalImg.src = "/static/images/ChatGPT_Image_9__202.png";
    }
    // Обновляем точки
    var dots = modalDots.querySelectorAll(".ec-modal__dot");
    dots.forEach(function (dot, index) {
      dot.classList.toggle("is-active", index === currentImageIndex);
    });
  }

  function buildDots() {
    modalDots.innerHTML = "";
    currentImages.forEach(function (_, index) {
      var dot = document.createElement("span");
      dot.className = "ec-modal__dot" + (index === 0 ? " is-active" : "");
      dot.setAttribute("data-index", index);
      dot.addEventListener("click", function () {
        currentImageIndex = parseInt(this.getAttribute("data-index"), 10);
        updateModalImage();
      });
      modalDots.appendChild(dot);
    });
  }

  // Открытие модального окна с данными из data-атрибутов карточки
  function openModal(card) {
    currentProduct = {
      id: card.getAttribute("data-id"),
      title: card.getAttribute("data-title"),
      price: card.getAttribute("data-price"),
      collectionTitle: card.getAttribute("data-collection-title"),
      type: card.getAttribute("data-category"),
      images: card.getAttribute("data-images")
        ? card.getAttribute("data-images").split(",")
        : [],
    };

    // Инициализация карусели
    currentImages = currentProduct.images;
    currentImageIndex = 0;
    updateModalImage();

    // Показать/скрыть стрелки и точки
    if (currentImages.length > 1) {
      modalPrev.style.display = "block";
      modalNext.style.display = "block";
      buildDots();
    } else {
      modalPrev.style.display = "none";
      modalNext.style.display = "none";
      modalDots.innerHTML = "";
    }

    // Заполняем остальные поля
    modalImg.alt = currentProduct.title;
    modalBadge.textContent = currentProduct.type;
    modalCollection.textContent = currentProduct.collectionTitle;
    modalName.textContent = currentProduct.title;
    modalPriceVal.textContent = formatPrice(currentProduct.price);
    modalBuy.classList.remove("is-loading");
    modalBuyLbl.textContent = "Купить";
    backdrop.classList.add("is-open");
    document.body.style.overflow = "hidden";
    modalClose.focus();
  }

  function closeModal() {
    backdrop.classList.remove("is-open");
    document.body.style.overflow = "";
    currentProduct = null;
  }

  backdrop.addEventListener("click", function (e) {
    if (e.target === backdrop) closeModal();
  });
  modalClose.addEventListener("click", closeModal);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && backdrop.classList.contains("is-open"))
      closeModal();
  });

  modalBuy.addEventListener("click", function () {
    if (modalBuy.classList.contains("is-loading")) return;
    modalBuy.classList.add("is-loading");
    modalBuyLbl.textContent = "Переход...";
    setTimeout(function () {
      window.location.href = "https://t.me/ermakwear";
    }, 300);
  });

  modalPrev.addEventListener("click", function () {
    if (currentImages.length === 0) return;
    currentImageIndex =
      (currentImageIndex - 1 + currentImages.length) % currentImages.length;
    updateModalImage();
  });

  modalNext.addEventListener("click", function () {
    if (currentImages.length === 0) return;
    currentImageIndex = (currentImageIndex + 1) % currentImages.length;
    updateModalImage();
  });

  // Обработка кликов по карточкам и кнопкам "Выбрать"
  collectionsEl.addEventListener("click", function (e) {
    var card = e.target.closest(".ec-card");
    if (card) {
      openModal(card);
    }
  });

  // Обработка клавиатуры для карточек
  collectionsEl.addEventListener("keydown", function (e) {
    if (e.key === "Enter" || e.key === " ") {
      var card = e.target.closest(".ec-card");
      if (card && document.activeElement === card) {
        e.preventDefault();
        openModal(card);
      }
    }
  });

  // Инициализация: фильтр "Все" активен по умолчанию
  setFilter("all");
})();

(function () {
  "use strict";

  var root = document.getElementById("ecAbout");
  if (!root) return;

  var advantages = root.querySelectorAll(".ec-advantage");
  var stats = root.querySelectorAll(".ec-about__stat");

  var prefersReduce =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function reveal(node, delay) {
    if (prefersReduce) {
      node.classList.add("is-visible");
      return;
    }
    setTimeout(function () {
      node.classList.add("is-visible");
    }, delay);
  }

  if (!("IntersectionObserver" in window) || prefersReduce) {
    advantages.forEach(function (n) {
      n.classList.add("is-visible");
    });
    stats.forEach(function (n) {
      n.classList.add("is-visible");
    });
    return;
  }

  var obs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var i = Array.prototype.indexOf.call(advantages, entry.target);
        reveal(entry.target, i >= 0 ? i * 120 : 0);
        obs.unobserve(entry.target);
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" },
  );

  var statsObs = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        var i = Array.prototype.indexOf.call(stats, entry.target);
        reveal(entry.target, i >= 0 ? i * 100 : 0);
        statsObs.unobserve(entry.target);
      });
    },
    { threshold: 0.2, rootMargin: "0px 0px -30px 0px" },
  );

  advantages.forEach(function (n) {
    obs.observe(n);
  });
  stats.forEach(function (n) {
    statsObs.observe(n);
  });
})();
