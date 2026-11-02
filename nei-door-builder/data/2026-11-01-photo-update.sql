alter table door_slabs add column if not exists shade_img text, add column if not exists gallery jsonb not null default '[]';
update door_slabs set shade_img='img/shade/P00-K01.png', photo_img='img/render/P00-K01.jpg', updated_at=now() where id='P00-K01';
update door_slabs set shade_img='img/shade/P01-LS01.png', photo_img=null, gallery='[{"img": "img/gallery/production-p02-i014.jpg", "caption": "Fangda production photo. Finish and glass shown may differ."}]'::jsonb, updated_at=now() where id='P01-LS01';
update door_slabs set shade_img='img/shade/P02-LS03.png', photo_img=null, updated_at=now() where id='P02-LS03';
update door_slabs set shade_img='img/shade/P02-LS04.png', photo_img=null, updated_at=now() where id='P02-LS04';
update door_slabs set shade_img='img/shade/P02-M01.png', photo_img='img/render/P02-M01.jpg', updated_at=now() where id='P02-M01';
update door_slabs set shade_img='img/shade/P02-M17.png', photo_img=null, updated_at=now() where id='P02-M17';
update door_slabs set shade_img='img/shade/P08-M02.png', photo_img=null, updated_at=now() where id='P08-M02';
update door_slabs set shade_img='img/shade/P03-K01.png', photo_img='img/render/P03-K01.jpg', updated_at=now() where id='P03-K01';
update door_slabs set shade_img='img/shade/P03-LS03.png', photo_img=null, updated_at=now() where id='P03-LS03';
update door_slabs set shade_img='img/shade/P04-LS02.png', photo_img=null, updated_at=now() where id='P04-LS02';
update door_slabs set shade_img='img/shade/P04-LS03.png', photo_img=null, updated_at=now() where id='P04-LS03';
update door_slabs set shade_img='img/shade/P05-LS01.png', photo_img=null, updated_at=now() where id='P05-LS01';
update door_slabs set shade_img='img/shade/P06-K01.png', photo_img='img/render/P06-K01.jpg', updated_at=now() where id='P06-K01';
update door_slabs set shade_img='img/shade/P05-LS02.png', photo_img=null, updated_at=now() where id='P05-LS02';
update door_slabs set shade_img='img/shade/P07-M01.png', photo_img=null, updated_at=now() where id='P07-M01';
update door_slabs set shade_img='img/shade/P08-K01.png', photo_img='img/render/P08-K01.jpg', updated_at=now() where id='P08-K01';
update door_slabs set shade_img='img/shade/CG02-K01.png', photo_img='img/render/CG02-K01.jpg', updated_at=now() where id='CG02-K01';
update door_slabs set shade_img='img/shade/FG02-LS05.png', photo_img=null, updated_at=now() where id='FG02-LS05';
update door_slabs set shade_img='img/shade/FG05-LS01.png', photo_img=null, updated_at=now() where id='FG05-LS01';
update door_slabs set shade_img='img/shade/FG06-LS01.png', photo_img=null, updated_at=now() where id='FG06-LS01';
update door_slabs set photo_img='img/render/FG02-M01.jpg', gallery='[{"img": "img/gallery/production-p01-i007.jpg", "caption": "Fangda production photo (full unit). Finish and glass shown may differ."}]'::jsonb, updated_at=now() where id='FG02-M01';
update door_slabs set photo_img='img/render/FG02-M07_SL.jpg', gallery='[{"img": "img/gallery/production-p01-i007.jpg", "caption": "Fangda production photo (full unit). Finish and glass shown may differ."}]'::jsonb, updated_at=now() where id='FG02-M07 SL';
update door_slabs set photo_img='img/render/P03-M01.jpg', gallery='[{"img": "img/gallery/production-p02-i004.jpg", "caption": "Fangda production photo. Finish and glass shown may differ."}]'::jsonb, updated_at=now() where id='P03-M01';
update door_slabs set photo_img=null, gallery='[{"img": "img/gallery/production-p03-i006.jpg", "caption": "Fangda production photo. Finish and glass shown may differ."}]'::jsonb, updated_at=now() where id='P02-M11';
update door_slabs set photo_img='img/render/P00-M02-N_SL.jpg', updated_at=now() where id='P00-M02-N SL';
update door_slabs set photo_img='img/render/P02-M15_SL.jpg', updated_at=now() where id='P02-M15 SL';
update door_slabs set photo_img='img/render/FG00-M01_SL.jpg', updated_at=now() where id='FG00-M01 SL';
update door_slabs set photo_img='img/render/P00-M01.jpg', updated_at=now() where id='P00-M01';
update door_slabs set photo_img='img/render/P02-M04.jpg', updated_at=now() where id='P02-M04';
update door_slabs set photo_img='img/render/P03-M02.jpg', updated_at=now() where id='P03-M02';
update door_slabs set photo_img='img/render/P08-M01.jpg', updated_at=now() where id='P08-M01';
update door_slabs set photo_img='img/render/P02-K03.jpg', updated_at=now() where id='P02-K03';
insert into door_slabs(id,code,collection,kind,label,lite,glass_box,lites,line_img,photo_img,shade_img,gallery,notes,sort) values ('P04-K03-TN','P04-K03-TN','K','door','4 Panel',null,null,'[]','img/line/P04-K03-TN.png','img/render/P04-K03-TN.jpg',null,'[]','Added from the catalog render label; drawing taken from the render.',900) on conflict (id) do nothing;
update door_slabs set photo_img='img/render/P02-K01_SL.jpg', updated_at=now() where id='P02-K01 SL';
insert into door_slabs(id,code,collection,kind,label,lite,glass_box,lites,line_img,photo_img,shade_img,gallery,notes,sort) values ('P00-LS02','P00-LS02','LS','door','Flush',null,null,'[]','img/line/P00-LS02.png','img/render/P00-LS02.jpg',null,'[]','Added from the catalog render label; drawing taken from the render.',900) on conflict (id) do nothing;
update door_slabs set photo_img='img/render/P02-LS02.jpg', updated_at=now() where id='P02-LS02';
update door_slabs set photo_img='img/render/P03-LS02.jpg', updated_at=now() where id='P03-LS02';
update door_slabs set photo_img='img/render/P04-LS01.jpg', updated_at=now() where id='P04-LS01';
update door_slabs set photo_img='img/render/P06-LS01.jpg', updated_at=now() where id='P06-LS01';
insert into door_slabs(id,code,collection,kind,label,lite,glass_box,lites,line_img,photo_img,shade_img,gallery,notes,sort) values ('P02-LS10 SL','P02-LS10','LS','sidelite','2 Panel sidelite',null,null,'[]','img/line/P02-LS10_SL.png','img/render/P02-LS10_SL.jpg',null,'[]','Added from the catalog render label; drawing taken from the render.',900) on conflict (id) do nothing;
update door_slabs set photo_img=null where photo_img like 'img/photo/%';
update door_finish_options set active=false where id not in ('U-M','U-K','U-LS','U-MS','U-F');
insert into door_finish_options(id,name,collections,kind,image,color,as_shipped,priced,sort,active) values
('FX-SMOOTH-PAINTING-WHITE','Smooth Painting White','{LS}','paint','img/finish/swatch_smooth_painting_white.jpg',null,false,false,20,true),
('FX-SMOOTH-PAINTING-BLACK','Smooth Painting Black','{LS}','paint','img/finish/swatch_smooth_painting_black.jpg',null,false,false,21,true),
('FX-SMOOTH-PAINTING-GREY','Smooth Painting Grey','{LS}','paint','img/finish/swatch_smooth_painting_grey.jpg',null,false,false,22,true),
('FX-SMOOTH-PAINTING-TAN','Smooth Painting Tan','{LS}','paint','img/finish/swatch_smooth_painting_tan.jpg',null,false,false,23,true),
('FX-BRUSH-SMOOTH-PAINTING-WHITE','Brush Smooth Painting White','{LS,MS}','paint','img/finish/swatch_brush_smooth_painting_white.jpg',null,false,false,24,true),
('FX-BRUSH-SMOOTH-PAINTING-BLACK','Brush Smooth Painting Black','{LS,MS}','paint','img/finish/swatch_brush_smooth_painting_black.jpg',null,false,false,25,true),
('FX-BRUSH-SMOOTH-PAINTING-GREY','Brush Smooth Painting Grey','{LS,MS}','paint','img/finish/swatch_brush_smooth_painting_grey.jpg',null,false,false,26,true),
('FX-BRUSH-SMOOTH-PAINTING-TAN','Brush Smooth Painting Tan','{LS,MS}','paint','img/finish/swatch_brush_smooth_painting_tan.jpg',null,false,false,27,true),
('FX-OAK-PAINTING-WHITE','Oak Painting White','{K}','paint','img/finish/swatch_oak_painting_white.jpg',null,false,false,28,true),
('FX-OAK-PAINTING-BLACK','Oak Painting Black','{K}','paint','img/finish/swatch_oak_painting_black.jpg',null,false,false,29,true),
('FX-OAK-PAINTING-GREY','Oak Painting Grey','{K}','paint','img/finish/swatch_oak_painting_grey.jpg',null,false,false,30,true),
('FX-OAK-PAINTING-TAN','Oak Painting Tan','{K}','paint','img/finish/swatch_oak_painting_tan.jpg',null,false,false,31,true),
('FX-OAK-STAINED-01','Oak Stained 01#','{K}','stain','img/finish/swatch_oak_stained_01.jpg',null,false,false,32,true),
('FX-OAK-STAINED-02','Oak Stained 02#','{K}','stain','img/finish/swatch_oak_stained_02.jpg',null,false,false,33,true),
('FX-OAK-STAINED-03','Oak Stained 03#','{K}','stain','img/finish/swatch_oak_stained_03.jpg',null,false,false,34,true),
('FX-OAK-STAINED-04','Oak Stained 04#','{K}','stain','img/finish/swatch_oak_stained_04.jpg',null,false,false,35,true),
('FX-MAHOGANY-PAINTING-WHITE','Mahogany Painting White','{M}','paint','img/finish/swatch_mahogany_painting_white.jpg',null,false,false,36,true),
('FX-MAHOGANY-PAINTING-BLACK','Mahogany Painting Black','{M}','paint','img/finish/swatch_mahogany_painting_black.jpg',null,false,false,37,true),
('FX-MAHOGANY-PAINTING-GREY','Mahogany Painting Grey','{M}','paint','img/finish/swatch_mahogany_painting_grey.jpg',null,false,false,38,true),
('FX-MAHOGANY-PAINTING-TAN','Mahogany Painting Tan','{M}','paint','img/finish/swatch_mahogany_painting_tan.jpg',null,false,false,39,true),
('FX-MAHOGANY-STAINED-01','Mahogany Stained 01#','{M}','stain','img/finish/swatch_mahogany_stained_01.jpg',null,false,false,40,true),
('FX-MAHOGANY-STAINED-02','Mahogany Stained 02#','{M}','stain','img/finish/swatch_mahogany_stained_02.jpg',null,false,false,41,true),
('FX-MAHOGANY-STAINED-03','Mahogany Stained 03#','{M}','stain','img/finish/swatch_mahogany_stained_03.jpg',null,false,false,42,true),
('FX-MAHOGANY-STAINED-04','Mahogany Stained 04#','{M}','stain','img/finish/swatch_mahogany_stained_04.jpg',null,false,false,43,true),
('FX-FIR-PAINTING-WHITE','Fir Painting White','{F}','paint','img/finish/swatch_fir_painting_white.jpg',null,false,false,44,true),
('FX-FIR-PAINTING-BLACK','Fir Painting Black','{F}','paint','img/finish/swatch_fir_painting_black.jpg',null,false,false,45,true),
('FX-FIR-PAINTING-GREY','Fir Painting Grey','{F}','paint','img/finish/swatch_fir_painting_grey.jpg',null,false,false,46,true),
('FX-FIR-PAINTING-TAN','Fir Painting Tan','{F}','paint','img/finish/swatch_fir_painting_tan.jpg',null,false,false,47,true),
('FX-FIR-STAINED-01','Fir Stained 01#','{F}','stain','img/finish/swatch_fir_stained_01.jpg',null,false,false,48,true),
('FX-FIR-STAINED-02','Fir Stained 02#','{F}','stain','img/finish/swatch_fir_stained_02.jpg',null,false,false,49,true),
('FX-FIR-STAINED-03','Fir Stained 03#','{F}','stain','img/finish/swatch_fir_stained_03.jpg',null,false,false,50,true),
('FX-FIR-STAINED-04','Fir Stained 04#','{F}','stain','img/finish/swatch_fir_stained_04.jpg',null,false,false,51,true) on conflict (id) do update set name=excluded.name,collections=excluded.collections,kind=excluded.kind,image=excluded.image,active=true;
update door_finish_options set name='Unfinished woodgrain (as shipped)' where id in ('U-M','U-K');update door_finish_options set name='Unfinished smooth, paint ready (as shipped)' where id='U-LS';update door_finish_options set name='Fir, as shipped' where id='U-F';
update door_collections set notes=trim(notes||' Brush Smooth finishes shown for LS and MS; Fangda''s swatch board does not say which collection they belong to. VERIFY.') where id='MS';