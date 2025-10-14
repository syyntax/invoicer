document.addEventListener('DOMContentLoaded', function() {
    const lineItemsTableBody = document.querySelector('#lineItemsTable tbody');
    const addLineItemBtn = document.getElementById('addLineItemBtn');
    const grandTotalElement = document.getElementById('grandTotal');
    const invoiceForm = document.getElementById('invoiceForm');
    const lineItemsJsonInput = document.getElementById('lineItemsJson');

    // Only proceed if elements exist (i.e., we are on the create/edit invoice page)
    if (!lineItemsTableBody) return;

    // Function to update the total for a single line item
    function updateLineItemTotal(row) {
        const quantityInput = row.querySelector('.item-quantity');
        const unitPriceInput = row.querySelector('.item-unit-price');
        const totalCell = row.querySelector('.item-total');

        const quantity = parseFloat(quantityInput.value) || 0;
        const unitPrice = parseFloat(unitPriceInput.value) || 0;
        const total = quantity * unitPrice;

        totalCell.textContent = total.toFixed(2);
        updateGrandTotal(); // Update grand total whenever a line item total changes
    }

    // Function to add a new line item row to the table
    window.addLineItem = function(item = {}) { // `item` is optional for pre-populating existing data
        const newRow = lineItemsTableBody.insertRow();
        newRow.innerHTML = `
            <td><input type="text" class="form-control item-description" value="${item.description || ''}" placeholder="Description" required></td>
            <td><input type="number" step="0.01" min="0" class="form-control item-quantity" value="${item.quantity ? item.quantity.toFixed(2) : '1.00'}" required></td>
            <td><input type="number" step="0.01" min="0" class="form-control item-unit-price" value="${item.unit_price ? item.unit_price.toFixed(2) : '0.00'}" required></td>
            <td class="item-total">${(item.total || 0).toFixed(2)}</td>
            <td><button type="button" class="btn btn-sm btn-danger remove-line-item" data-bs-toggle="tooltip" title="Delete Line Item"><i class="fas fa-trash-alt"></i></button></td>
        `;

        const quantityInput = newRow.querySelector('.item-quantity');
        const unitPriceInput = newRow.querySelector('.item-unit-price');
        const removeButton = newRow.querySelector('.remove-line-item');

        // Add event listeners for dynamic calculation
        quantityInput.addEventListener('input', () => updateLineItemTotal(newRow));
        unitPriceInput.addEventListener('input', () => updateLineItemTotal(newRow));
        
        // Add event listener for removing a line item
        removeButton.addEventListener('click', function() {
            newRow.remove();
            updateGrandTotal();
        });

        // Initialize tooltip for the new remove button
        new bootstrap.Tooltip(removeButton);

        // Update total for the new row immediately if data is provided
        if (item.quantity && item.unit_price) {
            updateLineItemTotal(newRow);
        }
    }

    // Function to calculate and update the grand total of all line items
    function updateGrandTotal() {
        let grandTotal = 0;
        document.querySelectorAll('#lineItemsTable tbody tr').forEach(row => {
            const totalCell = row.querySelector('.item-total');
            grandTotal += parseFloat(totalCell.textContent) || 0;
        });
        grandTotalElement.textContent = grandTotal.toFixed(2);
    }

    // Event listener for the "Add Line Item" button
    addLineItemBtn.addEventListener('click', () => addLineItem());

    // Event listener for form submission to gather line items and send as JSON
    invoiceForm.addEventListener('submit', function(event) {
        const lineItems = [];
        document.querySelectorAll('#lineItemsTable tbody tr').forEach(row => {
            lineItems.push({
                description: row.querySelector('.item-description').value,
                quantity: row.querySelector('.item-quantity').value,
                unit_price: row.querySelector('.item-unit-price').value,
                total: parseFloat(row.querySelector('.item-total').textContent)
            });
        });
        lineItemsJsonInput.value = JSON.stringify(lineItems);
    });

    // Initial grand total calculation (useful if page loads with existing items)
    updateGrandTotal();
});