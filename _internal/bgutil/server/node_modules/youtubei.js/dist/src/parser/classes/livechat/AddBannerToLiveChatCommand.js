import { YTNode } from '../../helpers.js';
import { Parser } from '../../index.js';
import LiveChatBanner from './items/LiveChatBanner.js';
export default class AddBannerToLiveChatCommand extends YTNode {
    static type = 'AddBannerToLiveChatCommand';
    banner;
    constructor(data) {
        super();
        this.banner = Parser.parseItem(data.bannerRenderer, LiveChatBanner);
    }
}
//# sourceMappingURL=AddBannerToLiveChatCommand.js.map