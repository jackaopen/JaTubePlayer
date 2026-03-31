import { YTNode } from '../helpers.js';
export default class PlayerLegacyDesktopYpcOffer extends YTNode {
    static type = 'PlayerLegacyDesktopYpcOffer';
    title;
    thumbnail;
    offer_description;
    offer_id;
    constructor(data) {
        super();
        this.title = data.itemTitle;
        this.thumbnail = data.itemThumbnail;
        this.offer_description = data.offerDescription;
        this.offer_id = data.offerId;
    }
}
//# sourceMappingURL=PlayerLegacyDesktopYpcOffer.js.map