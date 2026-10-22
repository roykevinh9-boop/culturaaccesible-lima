import {CatalogModel} from '../../models/catalog-model.js';
import {CatalogView} from '../../views/catalog-view.js';
import {CatalogController} from '../../controllers/catalog-controller.js';

const application=new CatalogController(new CatalogModel(),new CatalogView());
application.start();
