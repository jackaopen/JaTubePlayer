const DEFAULT_PORT = 5000;

 function isMediaUrl(rawUrl) {
    try {
      const url = new URL(rawUrl);
      const host = url.hostname;

      if (host === "youtube.com" || host === "www.youtube.com") {
        return (
          (url.pathname === "/watch" && url.searchParams.has("v")) ||
          url.pathname.startsWith("/shorts/")
        );
      }
      if (host === "youtu.be") {
        return url.pathname.length > 1;
      }
      if (host === "twitch.tv" || host === "www.twitch.tv") {
        return url.pathname !== "/";
      }

      return false;
    } catch {
      return false;
    }
  }

chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "dir",
        title: "🎬Directly send to JTP",
        contexts: ["link","page"],
        documentUrlPatterns : ["https://www.youtube.com/*","https://www.twitch.tv/*"]

  });
  chrome.contextMenus.create({
        id: "star",
        title: "⭐ Star on JTP",
        contexts: ["link","page"],
        documentUrlPatterns : ["https://www.youtube.com/*","https://www.twitch.tv/*"]

  });
  chrome.contextMenus.create({
        id: "add_to_end",
        title: "➕ Add to JTP playlist",
        contexts: ["link","page"],
        documentUrlPatterns : ["https://www.youtube.com/*","https://www.twitch.tv/*"]

  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
    const { port = DEFAULT_PORT } =
      await chrome.storage.local.get("port");

      
    const urlToSend = info.linkUrl || info.pageUrl;
    if(isMediaUrl(urlToSend)){
      try {
          const res = await fetch(`http://localhost:${port}/receive_url/${info.menuItemId}`, {
              method: "POST",                              
              headers: {"X-auth":"Jatubeplayerextensionbyjackaopen"}, 
              body: urlToSend
        });
        if (!res.ok) {
          const message = await res.text();
          chrome.notifications.create({
            type:"basic",
            iconUrl:"err.png",
            message,
            title:'Jatubeplayer extension error'
          });
        }
        
      } catch (err) {
        chrome.notifications.create({
          type:"basic",
          iconUrl:"err.png",
          message: "We can't seems to send the url to the Jatubeplayer",
          title:'Jatubeplayer extension error'
      });
      }
    }
    else {
      chrome.notifications.create({
        type:"basic",
        iconUrl:"err.png",
        message:'You cant send the youtube home page url, try to click on a video?',
        title:"Jatubeplayer extension error"

      })
    }
  });
  

    
  
