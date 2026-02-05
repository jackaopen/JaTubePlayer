chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "sendToJTP",
        title: "🎬 Send to JTP",
        contexts: ["link","page"],
        documentUrlPatterns : ["https://www.youtube.com/*"]

  });
});

chrome.contextMenus.onClicked.addListener( async (info, tab) => {
  if (info.menuItemId == "sendToJTP") {
    const urlToSend = info.linkUrl || info.pageUrl;
    if(urlToSend != "https://www.youtube.com/"){
      try {
          res = await fetch("http://localhost:5000/receive_url", {
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
    }
    else {
      chrome.notifications.create({
        type:"basic",
        iconUrl:"err.png",
        message:'You cant send the youtube home page url, try to click on a video?',
        title:"Jatubeplayer extension error"

      })
    }
  
  
  
  
  }
  });
  

    
  