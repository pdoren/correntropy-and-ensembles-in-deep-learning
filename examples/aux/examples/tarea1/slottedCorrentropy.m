function [lag,v,sigma,c] = slottedCorrentropy(t,x)
    [t,I] = sort(t,'ascend');
    x = x(I);
    N=length(t);
    sigma = 2*1.06*std(x)*power(N,-0.2);
    msr = (t(end) - t(1))/N;
    ss = msr*0.1;
    max_lag = 0.2*(t(end)-t(1))/ss;
    %max_lag = 0.75*(t(end)-t(1))/ss; %spectrogram
    %ss = ss*5;
    dt = repmat(t,N,1);
    dt = (dt - dt')';
    dt = dt(tril(true(size(dt))));
    dx = repmat(x,N,1);
    dxC = dx.*dx';
    dx = (dx - dx')';    
    dx = dx(tril(true(size(dx))));
    dxC = dxC(tril(true(size(dxC))));
    [dt,I] = sort(dt,'ascend');
    dx = dx(I);
    dxC=dxC(I);
    Gx = exp(-0.5*dx.^2/sigma^2);
    v = zeros(size(0:max_lag));
    c = zeros(size(0:max_lag));
    lag = zeros(size(0:max_lag));
    for k = 0:max_lag
        index = find( abs(dt -k*ss) < ss*5);
        Gw = 1/(2*pi*ss)*exp(-0.5*(dt(index) - k*ss).^2/ss^2);
        lag(k+1) = sum(Gw.*dt(index))/sum(Gw);
        v(k+1) = sum(Gw.*Gx(index))/sum(Gw);
        c(k+1) = sum(Gw.*dxC(index))/sum(Gw);
    end
    empty = ~isnan(lag);
    lag = lag(empty);
    v = v(empty);
    c = c(empty);
    c = c/var(x);
end
