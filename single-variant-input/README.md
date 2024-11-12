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

