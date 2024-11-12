# Single Variant Input

This javascript widget to accept any single variant and link out to the OC single variant page. Accepted inputs are genomic coordinates, hgvs, dbsnp, and ClinGen Allele Registry.

To use, include or link to the javascript and css file, and add a `<div id='oc-svi'></div>` tag to your html.

## title

You can use the `title` attribute of the oc-svi div to give an alternate header.

## Fallback Content

If you are importing the js and css from another server, you may want to include html within the oc-svi div. This will be displayed until the js file is loaded, and can be used as fallback content if the widget cannot be loaded.

```html
<div id="oc-svi">
    <style>
        #oc-svi h1 {
            text-decoration: underline;
        }
    </style>
    <h1>Fallback Content Header</h1>
    <div>This will be shown until the widget is loaded from the server</div>
</div>
```

## Custom submission handling

By default, the input form will parse the input and generate a url to the OC Single Variant page and open the link in a new window.

To change the behavior, you can handle a custom event emitted by the form that occurs after the input has been validated and parsed. To do this, add `class='custom-handler'` to the oc-svi div. Then, add an event handler for the `variantSubmit` event. The event handler should accept the event object, and the variant information will be store in `event.detail`.

```javascript
document.getElementById('oc-svi').addEventListener('variantSubmit', (event) => {
    const assembly = event.detail['assembly'];
    const chrom = event.detail['chrom'];
    const pos = event.detail['pos'];
    const ref_base = event.detail['ref_base'];
    const alt_base = event.detail['alt_base'];
    const hgvs = event.detail['hgvs'];
    const clingen = event.detail['clingen'];
    const dbsnp = event.detail['dbsnp'];
});
```