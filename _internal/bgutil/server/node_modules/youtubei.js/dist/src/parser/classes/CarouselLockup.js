import { YTNode } from '../helpers.js';
import InfoRow from './InfoRow.js';
import { Parser } from '../index.js';
import CompactVideo from './CompactVideo.js';
export default class CarouselLockup extends YTNode {
    static type = 'CarouselLockup';
    info_rows;
    video_lockup;
    constructor(data) {
        super();
        this.info_rows = Parser.parseArray(data.infoRows, InfoRow);
        this.video_lockup = Parser.parseItem(data.videoLockup, CompactVideo);
    }
}
//# sourceMappingURL=CarouselLockup.js.map