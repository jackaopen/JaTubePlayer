(() => {
    const clean = element => (element?.textContent || "").trim();
    const visible = element => {
        if (!element) return false;
        const rect = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        return rect.width > 0 && rect.height > 0 &&
            style.display !== "none" && style.visibility !== "hidden";
    };

    const ignoredText = new Set([
        "Skip navigation", "Home", "Shorts", "Subscriptions", "You", "History"
    ]);
    const ignoredArea = [
        "ytd-masthead", "ytd-guide-renderer", "ytd-mini-guide-renderer",
        "#guide", "#masthead-container"
    ].join(",");

    const nameSpans = [...document.querySelectorAll(
        "span.ytAttributedStringHost.ytAttributedStringWhiteSpacePreWrap[role='text']"
    )];
    const nameElement = nameSpans.find(element => {
        const value = clean(element);
        return value && value.length <= 80 && !ignoredText.has(value) &&
            !element.closest(ignoredArea) && visible(element);
    });

    // On /feed/you, use the profile avatar in the page header. This avoids
    // confusing it with the top-bar avatar or a channel/video thumbnail.
    const feedAvatarSelector = "#page-header > yt-page-header-renderer > yt-page-header-view-model > div > div.ytPageHeaderViewModelHeadline > yt-decorated-avatar-view-model > yt-avatar-shape > div > div > div > img:nth-child(1)";
    const feedAvatarXPath = "/html/body/ytd-app/div[1]/ytd-page-manager/ytd-browse/div[4]/ytd-tabbed-page-header/div/div/yt-page-header-renderer/yt-page-header-view-model/div/div[1]/yt-decorated-avatar-view-model/yt-avatar-shape/div/div/div/img[1]";
    const feedAvatarByCss = document.querySelector(feedAvatarSelector);
    const feedAvatarByXPath = document.evaluate(
        feedAvatarXPath,
        document,
        null,
        XPathResult.FIRST_ORDERED_NODE_TYPE,
        null
    ).singleNodeValue;

    // A shorter structural selector survives harmless wrapper/class changes.
    const feedAvatarByStructure = document.querySelector(
        "#page-header yt-page-header-view-model yt-decorated-avatar-view-model yt-avatar-shape img"
    );

    // Keep selectors as fallbacks in case YouTube changes the page hierarchy.
    const fallbackAvatar = [
        "button#avatar-btn img",
        "#avatar-btn img",
        "ytd-topbar-menu-button-renderer img",
        "img[src*='yt3.googleusercontent.com']",
        "img[src*='yt3.ggpht.com']"
    ].map(selector => document.querySelector(selector)).find(Boolean);

    const name = clean(nameElement);
    // Do not require visibility here. The host deliberately hides this WebView
    // while reading /feed/you, which can make a valid image fail layout checks.
    const avatarElement = [
        feedAvatarByCss,
        feedAvatarByXPath,
        feedAvatarByStructure,
        fallbackAvatar
    ].find(Boolean);
    const srcsetFirstUrl = (avatarElement?.getAttribute("srcset") || "")
        .split(",")[0]
        .trim()
        .split(/\s+/)[0];
    const avatar = avatarElement?.currentSrc ||
        avatarElement?.src ||
        avatarElement?.getAttribute("src") ||
        avatarElement?.getAttribute("data-src") ||
        avatarElement?.getAttribute("data-thumb") ||
        srcsetFirstUrl ||
        "";
    return [name, avatar];
})()
