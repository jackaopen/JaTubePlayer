import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import StructuredDescriptionPlaylistLockup from './StructuredDescriptionPlaylistLockup.js';
import Text from './misc/Text.js';
export default class VideoDescriptionCourseSection extends YTNode {
    static type = 'VideoDescriptionCourseSection';
    section_title;
    media_lockups;
    constructor(data) {
        super();
        this.section_title = new Text(data.sectionTitle);
        this.media_lockups = Parser.parseArray(data.mediaLockups, [StructuredDescriptionPlaylistLockup]);
    }
}
//# sourceMappingURL=VideoDescriptionCourseSection.js.map