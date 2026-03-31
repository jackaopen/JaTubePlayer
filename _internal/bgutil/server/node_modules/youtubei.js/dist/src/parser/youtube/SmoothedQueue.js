/**
 * Flattens the given queue.
 * @param queue - The queue to flatten.
 */
function flattenQueue(queue) {
    const nodes = [];
    for (const group of queue) {
        if (Array.isArray(group)) {
            for (const node of group) {
                nodes.push(node);
            }
        }
        else {
            nodes.push(group);
        }
    }
    return nodes;
}
class DelayQueue {
    front;
    back;
    constructor() {
        this.front = [];
        this.back = [];
    }
    isEmpty() {
        return !this.front.length && !this.back.length;
    }
    clear() {
        this.front = [];
        this.back = [];
    }
    getValues() {
        return this.front.concat(this.back.reverse());
    }
}
export default class SmoothedQueue {
    #last_update_time;
    #estimated_update_interval;
    #callback;
    #action_queue;
    #next_update_id;
    #poll_response_delay_queue;
    constructor() {
        this.#last_update_time = null;
        this.#estimated_update_interval = null;
        this.#callback = null;
        this.#action_queue = [];
        this.#next_update_id = null;
        this.#poll_response_delay_queue = new DelayQueue();
    }
    enqueueActionGroup(group) {
        if (this.#last_update_time !== null) {
            const delay = Date.now() - this.#last_update_time;
            this.#poll_response_delay_queue.back.push(delay);
            if (5 < (this.#poll_response_delay_queue.front.length + this.#poll_response_delay_queue.back.length)) {
                if (!this.#poll_response_delay_queue.front.length) {
                    this.#poll_response_delay_queue.front = this.#poll_response_delay_queue.back;
                    this.#poll_response_delay_queue.front.reverse();
                    this.#poll_response_delay_queue.back = [];
                }
                this.#poll_response_delay_queue.front.pop();
            }
            this.#estimated_update_interval = Math.max(...this.#poll_response_delay_queue.getValues());
        }
        this.#last_update_time = Date.now();
        this.#action_queue.push(group);
        if (this.#next_update_id === null) {
            this.#next_update_id = setTimeout(this.emitSmoothedActions.bind(this));
        }
    }
    emitSmoothedActions() {
        this.#next_update_id = null;
        if (this.#action_queue.length) {
            let delay = 1E4;
            if (this.#estimated_update_interval !== null && this.#last_update_time !== null) {
                delay = this.#estimated_update_interval - Date.now() + this.#last_update_time;
            }
            delay = this.#action_queue.length < delay / 80 ? 1 : Math.ceil(this.#action_queue.length / (delay / 80));
            const actions = flattenQueue(this.#action_queue.splice(0, delay));
            if (this.#callback) {
                this.#callback(actions);
            }
            if (this.#action_queue !== null) {
                if (delay == 1) {
                    delay = this.#estimated_update_interval / this.#action_queue.length;
                    delay *= Math.random() + 0.5;
                    delay = Math.min(1E3, delay);
                    delay = Math.max(80, delay);
                }
                else {
                    delay = 80;
                }
                this.#next_update_id = setTimeout(this.emitSmoothedActions.bind(this), delay);
            }
        }
    }
    clear() {
        if (this.#next_update_id !== null) {
            clearTimeout(this.#next_update_id);
            this.#next_update_id = null;
        }
        this.#action_queue = [];
    }
    set callback(cb) {
        this.#callback = cb;
    }
    get callback() {
        return this.#callback;
    }
    get action_queue() {
        return this.#action_queue;
    }
    get estimated_update_interval() {
        return this.#estimated_update_interval;
    }
    get last_update_time() {
        return this.#last_update_time;
    }
    get next_update_id() {
        return this.#next_update_id;
    }
    get poll_response_delay_queue() {
        return this.#poll_response_delay_queue;
    }
}
//# sourceMappingURL=SmoothedQueue.js.map