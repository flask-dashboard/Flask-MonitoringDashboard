export default function () {

    this.init = function (name) {
        this.page = 1;
        this.perPage = 5;
        this.total = 0;
        this.name = name;
    };

    this.maxPages = function () {
        return Math.ceil(this.total / this.perPage);
    };

    this.onReload = function () {
    };

    this.getLeft = function () {
        return (this.page - 1) * this.perPage;
    };

    this.getRight = function () {
        return Math.min(this.total, this.getLeft() + this.perPage);
    };

    this.getFirstPage = function () {
        let pages = this.getPages();
        return pages.length > 0 ? pages[0] : this.page;
    };

    this.getLastPage = function () {
        let pages = this.getPages();
        return pages.length > 0 ? pages[pages.length - 1] : this.page;
    };

    this.goto = function (p) {
        this.page = p;
        this.onReload();
    };

    this.setTotal = function (t) {
        this.total = t;
        this.onReload();
    };

    this.getPages = function () {
        let left = this.page - 1;
        let right = this.page + 1;
        let range = [];

        if (left <= 0) {
            right -= left - 1;
            left = 1;
        }
        if (right > this.maxPages()) {
            right = this.maxPages();
        }

        if (left == 2) {
            range.push(1);
        } else if (left == 3) {
            range.push(1, 2);
        } else if (left > 3) {
            range.push(1, '...');
        }

        for (let i = left; i <= right; i++) {
            range.push(i);
        }
        if (this.maxPages() - right > 2) {
            range.push('...', this.maxPages());
        } else if (this.maxPages() - right == 2) {
            range.push(this.maxPages() - 1, this.maxPages());
        } else if (this.maxPages() - right == 1) {
            range.push(this.maxPages());
        }
        return range;
    }
};
