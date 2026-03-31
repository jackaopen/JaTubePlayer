import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import { Text } from '../misc.js';
import CarouselLockup from './CarouselLockup.js';
export default class VideoDescriptionMusicSection extends YTNode {
    static type = 'VideoDescriptionMusicSection';
    carousel_lockups;
    section_title;
    constructor(data) {
        super();
        this.carousel_lockups = Parser.parseArray(data.carouselLockups, CarouselLockup);
        this.section_title = new Text(data.sectionTitle);
    }
}
//# sourceMappingURL=VideoDescriptionMusicSection.js.map