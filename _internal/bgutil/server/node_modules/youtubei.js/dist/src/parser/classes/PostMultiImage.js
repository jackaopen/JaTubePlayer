import { Parser } from '../index.js';
import BackstageImage from './BackstageImage.js';
import { YTNode } from '../helpers.js';
export default class PostMultiImage extends YTNode {
    static type = 'PostMultiImage';
    images;
    constructor(data) {
        super();
        this.images = Parser.parseArray(data.images, BackstageImage);
    }
}
//# sourceMappingURL=PostMultiImage.js.map