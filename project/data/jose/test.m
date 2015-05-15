%% setup directorios
INIT_POS = 10;
IMAGE_STEP = 4;
SAVE_DIR = 'c:\restemp\prior\';
SAVE_EXTENSION = 'JPG';
SAVE_EXTENSION_PRIOR = 'BMP';%para evitar compresion en las mascaras
DIR = 'C:\temp\';
DIR = 'C:\temp\C TRAMO 3 TUNEL\';
%files = [dir([DIR '*.16raw']);dir([DIR '*.16zip'])];
files = [dir([DIR '*.16zip'])];



GPScoords =gpsRead(DIR,files(1).name);
currentLon = GPScoords(1);
currentLat = GPScoords(2);
currentHeight = GPScoords(3);



%% cargamos la trayectoria que ha hecho el coche
Trayectoria = [];
newRoad = [];
for i=1:length(files),
 [Trayectoria(i,:),temp] = gpsRead(DIR,files(i).name);
 SignalValid(i) = temp(1);
end

%% INICIALIZAcIONES VARIAS
% Route Definition

% Generate Reference
g2r=pi/180;
[EARTHa,EARTHb,EARTHe2,finv] = refell('WGS84');
% %Barcelona  Cerdanyola 	Lat=41.30 N  Lon=2.09 E  H=81m
Lat0=g2r*41.4818;
Lon0=g2r* 2.0470;
H0=81.0;
Lat0y=Lat0+0.01;
Lon0x=Lon0+0.01;
H0z=H0+0.01;
[x0,z0,y0] = ell2xyz_2(Lat0,Lon0,H0,EARTHa,EARTHe2);
[x0x,z0x,y0x] = ell2xyz_2(Lat0,Lon0x,H0,EARTHa,EARTHe2);
[x0y,z0y,y0y] = ell2xyz_2(Lat0y,Lon0,H0,EARTHa,EARTHe2);
[x0z,z0z,y0z] = ell2xyz_2(Lat0,Lon0,H0z,EARTHa,EARTHe2);

r=[x0,y0,z0];
vx=[x0x,y0x,z0x]-r;
vx=vx/norm(vx);
vy=[x0y,y0y,z0y]-r;
vy=vy/norm(vy);
vz=[x0z,y0z,z0z]-r;
vz=vz/norm(vz);
%improving orthogonality
vx=vx-vy*(vx*vy');
vx=vx/norm(vx);
vz=vz-vy*(vz*vy');
vz=vz/norm(vz);
vz=vz-vx*(vz*vx');
vz=vz/norm(vz);
Mcb=[vx -r*vx'; vy -r*vy'; vz -r*vz'; 0 0 0 1]; 


%% Generate Roads
FORZARZ0=true;
routes.points=[];
routes.index_l=[];
routes.index_m=[];
routes.index_r=[];
routes.colors=[];

for ro=1:length(roads);
    Lat=g2r*roads(ro).Y(1:end-1);
    Lon=g2r*roads(ro).X(1:end-1);
    H=H0+zeros(size(Lon)); 
    [x,z,y] = ell2xyz_2(Lat,Lon,H,EARTHa,EARTHe2);
    vtmp=[x;y;z;ones(1,length(x))];% [x(end);y(end);z(end);1]]; 
    tp=Mcb*vtmp; %trajectory points sobre un plano (casi, z varia poco)

    if(FORZARZ0)
        tp=[tp(1,:); tp(2,:); zeros(size(tp(3,:))); ones(size(tp(1,:)))];
    else
        tp=[tp(1,:); tp(2,:); tp(3,:);              ones(size(tp(1,:)))];
    end

    %Reparametrization with constant step
    step=PATCHLENGTH; %m
    len=0;
%    t=zeros(length(tp),1);
    t=zeros(size(tp,2),1);
    for i=2:size(tp,2)
        d=tp(1:3,i)-tp(1:3,i-1);
        len=len+sqrt(sum(d.^2));
        t(i)=len;
    end
    tt=0:step:len;    
    try
        p=interp1(t,tp',tt,'lineal')';
%        p=interp1(t,tp',tt,'cubic')';
    catch
        p=tp(1,:);
        disp('skkipping plot');
        %si entramos aqui el plot no acaba de ir bien.
    end
    
             figure(1)
            hold on
            plot(tp(1,:),tp(2,:),'bs-')
            plot(p(1,:),p(2,:),'g.')
            hold off
            axis equal

 %monto los puntos de la carretera
    if(strcmp(roads(ro).type,'motorway')) 
        W = 2*3.5; %m calzada
        M = 1.0; %m cuneta
        disp('motorway');
    elseif (strcmp(roads(ro).type,'residential'))
        W = 1*3.5; %m calzada
        M = 0.5; %m cuneta
        disp('residential');
    elseif (strcmp(roads(ro).type,'trunk'))
        W = 4*3.5; %m calzada
        M = 1.0; %m cuneta
        disp('trunk');
    elseif (strcmp(roads(ro).type,'tertiary'))
        W = 2*3; %m calzada
        M = 0.3; %m cuneta
        disp('tertiary');
    elseif (strcmp(roads(ro).type,'secondary'))
        W = 2*3.5; %m calzada
        M = 0.5; %m cuneta
        disp('secondary');
    elseif (strcmp(roads(ro).type,'auxiliar'))
        W = 1*3.5; %m calzada
        M = 1.0; %m cuneta
        disp('auxiliar');
    else        
        W = 1*3.5; %m calzada
        M = 1.0; %m cuneta
        disp('road type: not defined-- Using defaults');
    end

    %    pl2 (M) pl (W) pr (M) pr2    
    pc=[p(:,1) p(:,1) p(:,1) p(:,1)];
    index_l=[1 2 2 1];
    index_m=[2 3 3 2];
    index_r=[3 4 4 3];
    colors = [[0 0 0]; [1 1 1]; [1 1 1]; [0 0 0]];
    if size(p,1)>1,
        for i=2:size(p,2)
            vn=p(1:3,i)-p(1:3,i-1);
            vt=cross(vn,[0 0 1]');
            vt=vt/norm(vt);
            vl2=[-(M+W/2)*vt; 0];
            vl =[  -(W/2)*vt; 0];
            vr =[   (W/2)*vt; 0];
            vr2=[ (M+W/2)*vt; 0];
            pc=[pc p(:,i)+vl2 p(:,i)+vl p(:,i)+vr p(:,i)+vr2];

            index_l=[index_l; [1 2 6 5]+(i-2)*4];
            index_m=[index_m; [2 3 7 6]+(i-2)*4];
            index_r=[index_r; [3 4 8 7]+(i-2)*4];

           % colors=[colors; [0 0 0]; [1 1 1]; [1 1 1]; [0 0 0]];
            colors=[colors; [1 1 1]; [1 1 1]; [1 1 1]; [1 1 1]];
        end
        routes.points=[routes.points pc];
        routes.index_l=[routes.index_l; index_l+4*length(routes.index_l)];
        routes.index_m=[routes.index_m; index_l+4*length(routes.index_m)];
        routes.index_r=[routes.index_r; index_l+4*length(routes.index_r)];
        routes.colors=[routes.colors; colors];
    end
end


    

%% gestion de la trayectoria del coche
%  Trayectoria del coche

Lat=g2r*Trayectoria(:,1)';
Lon=g2r*Trayectoria(:,2)';
H=Trayectoria(:,3)'; 

MEMORY = 50;
Step = zeros(MEMORY,2);
index = 1;
for i=1:length(SignalValid),
    if SignalValid(i) == 1,
        %aculumlamso
        Step(index,:) = [Lat(i) Lon(i)];
        index = index +1;
        if index > MEMORY,
            index=1;
        end
    else
       temp =(unique(Step,'rows'));
       difference = mean(temp(2:end,:) - temp(1:end-1,:))/10;
       %14 frames por segundo.. asi emulamos que cogemos cada vez
       Lat(i) = Lat(i-1) + difference(1);
       Lon(i) = Lon(i-1) + difference(2);
    end
        
    
end

