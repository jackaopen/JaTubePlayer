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

chrome.contextMenus.onClicked.addListener( async (info, tab) => {
  
  var mode = '';
  if (info.menuItemId == "dir") {
    mode = "dir";
  }
  if (info.menuItemId == "star") {
    mode = "star";
  }
  else if (info.menuItemId == "add_to_end") {
    mode = "add_to_end";
  }


    const urlToSend = info.linkUrl || info.pageUrl;
    if(urlToSend != "https://www.youtube.com/"){
      try {
          res = await fetch("http://localhost:5000/receive_url/"+mode, {
              method: "POST",                              
              headers: {"X-auth":"Jatubeplayerextensionbyjackaopen"}, 
              body: urlToSend
        });
        if (res.text == 'invalid url') {
          chrome.notifications.create({
            type:"basic",
            iconUrl:"err.png",
            message: "The url is invalid",
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
      finally {
        mode = '';
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
  

    
  