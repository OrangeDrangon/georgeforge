(function () {
    "use strict";

    $(document).ready(function () {
        const table = $("#table-store").DataTable({
            language: { url: "{{ DT_LANG_PATH }}" },
            order: [[0, "asc"]],
            pageLength: 25,
            lengthMenu: [
                [10, 25, 50, 100],
                [10, 25, 50, 100],
            ],
            stateSave: true,
            stateDuration: 0,
            columnDefs: [
                { visible: false, targets: [0, 1] },
                { orderable: false, targets: [2, 3, 4, 5, 6] },
            ],
            drawCallback: function (settings) {
                const api = this.api();
                let last = null;

                api.rows({ page: "current" }).every(
                    function (rowIdx, tableLoop, rowLoop) {
                        const group = $(this.node()).data("group");

                        if (last !== group) {
                            $(this.node()).before(
                                '<tr class="group-row"><th colspan="6" class="bg-primary text-white">' +
                                    group +
                                    "</th></tr>",
                            );
                            last = group;
                        }
                    },
                );
            },
        });
    });
})();
