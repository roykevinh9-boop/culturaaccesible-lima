import {CatalogModel} from './model.js';
import {CatalogView} from './view.js';
import {CatalogPresenter} from './presenter.js';

const application=new CatalogPresenter(new CatalogModel(),new CatalogView());
application.start();
