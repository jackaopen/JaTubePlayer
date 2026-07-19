(() => {
      const text = element => element?.textContent?.trim() || "";

      const firstMatch = (root, selectors) =>
          selectors
              .map(selector => root?.querySelector(selector))
              .find(Boolean);

      const header = document.querySelector("#page-header");

      const name = [...(header?.querySelectorAll("span[role='text']") || [])]
          .map(text)
          .find(Boolean) || "";

      const avatar = firstMatch(header, [
          "yt-avatar-shape img",
          "yt-decorated-avatar-view-model img",
          "img[src*='googleusercontent.com']"
      ]) || firstMatch(document, [
          "#avatar-btn img",
          "ytd-topbar-menu-button-renderer img"
      ]);

      const srcsetUrl = avatar?.srcset
          ?.split(",")[0]
          .trim()
          .split(/\s+/)[0];

      const avatarUrl =
          avatar?.currentSrc ||
          avatar?.src ||
          avatar?.dataset.src ||
          avatar?.dataset.thumb ||
          srcsetUrl ||
          "";

      return [name, avatarUrl];
  })()