import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import Button from './Button.js';
export default class CopyLink extends YTNode {
    static type = 'CopyLink';
    copy_button;
    short_url;
    style;
    constructor(data) {
        super();
        this.copy_button = Parser.parseItem(data.copyButton, Button);
        this.short_url = data.shortUrl;
        this.style = data.style;
    }
}
//# sourceMappingURL=CopyLink.js.map