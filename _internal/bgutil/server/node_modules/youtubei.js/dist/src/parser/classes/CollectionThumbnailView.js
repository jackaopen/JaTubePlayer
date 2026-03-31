import { YTNode } from '../helpers.js';
import { Parser } from '../index.js';
import ThumbnailView from './ThumbnailView.js';
export default class CollectionThumbnailView extends YTNode {
    static type = 'CollectionThumbnailView';
    primary_thumbnail;
    stack_color;
    constructor(data) {
        super();
        this.primary_thumbnail = Parser.parseItem(data.primaryThumbnail, ThumbnailView);
        if (data.stackColor) {
            this.stack_color = {
                light_theme: data.stackColor.lightTheme,
                dark_theme: data.stackColor.darkTheme
            };
        }
    }
}
//# sourceMappingURL=CollectionThumbnailView.js.map