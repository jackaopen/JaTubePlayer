(() => {
    const badText = new Set([
        "Skip navigation", "略過導覽功能",
        "Home", "首頁",
        "Shorts",
        "Subscriptions", "訂閱內容",
        "You", "你的內容",
        "History", "觀看紀錄"
    ]);

    const badArea = [
        "ytd-masthead",
        "ytd-guide-renderer",
        "ytd-mini-guide-renderer",
        "#guide",
        "#masthead-container"
    ].join(",");

    const clean = element => (element.textContent || "").trim();
    const visible = element => {
        const rect = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        return rect.width > 0 && rect.height > 0 && style.display !== "none" && style.visibility !== "hidden";
    };

    const valid = element => {
        const text = clean(element);
        return text &&
            text.length <= 80 &&
            !badText.has(text) &&
            !element.closest(badArea) &&
            visible(element);
    };

    const spans = [...document.querySelectorAll(
        "span.ytAttributedStringHost.ytAttributedStringWhiteSpacePreWrap[role='text']"
    )];

    const name = clean(spans.find(valid));
    const avatar = document.querySelector("img[src*='yt3.ggpht.com']")?.src || "";

    return {
        user_name: name,
        user_mail: "",
        user_avatar: avatar,
        debug: {
            url: location.href,
            exactSpanCount: spans.length,
            nameSpanFound: !!name
        }
    };
})()
