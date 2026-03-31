import { Parser } from '../index.js';
import { YTNode } from '../helpers.js';
import Button from './Button.js';
import Text from './misc/Text.js';
import Thumbnail from './misc/Thumbnail.js';
export default class RecognitionShelf extends YTNode {
    static type = 'RecognitionShelf';
    title;
    subtitle;
    avatars;
    button;
    surface;
    constructor(data) {
        super();
        this.title = new Text(data.title);
        this.subtitle = new Text(data.subtitle);
        this.avatars = data.avatars.map((avatar) => new Thumbnail(avatar));
        this.button = Parser.parseItem(data.button, Button);
        this.surface = data.surface;
    }
}
//# sourceMappingURL=RecognitionShelf.js.map