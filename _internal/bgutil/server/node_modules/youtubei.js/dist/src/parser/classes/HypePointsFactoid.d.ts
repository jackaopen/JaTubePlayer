import { type RawNode } from '../index.js';
import { YTNode } from '../helpers.js';
import Factoid from './Factoid.js';
export default class HypePointsFactoid extends YTNode {
    static type: string;
    factoid: Factoid | null;
    constructor(data: RawNode);
}
