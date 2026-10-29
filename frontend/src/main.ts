console.log ("hello world!")

class Square{
    side:number;

    constructor (side: number){
        this.side=side;
    }
    getArea(){
        return this.side*this.side;
    }
    getName(){
        return "Square";
    }
}
class Rektanable{
    width:number;
    height:number;
    constructor (width:number, height:number){
        this.width=width;
        this.height=height;
    }
    getArea(){
            return this.height*this.width;
    }
    getName(){
        return "Rektanable";
    }
}
class Circle{
    radius:number;
    constructor (radius:number){
        this.radius=radius;
    }
    getArea(){
        return this.radius*this.radius*3.14
    }
    getName(){
        return "Circle";
    }
}
const s=new Square(5)
const r=new Rektanable(5, 10)
const c=new Circle(10)
console.log(s, r, c)
console.log(
    "Я " + s.getName() + ", моя площадь " + s.getArea().toString()+'\n',
    "Я " + r.getName() + ", моя площадь " + r.getArea().toString()+'\n',
    "Я " + c.getName() + ", моя площадь " + c.getArea().toString()+'\n')
    


const x=[7, 8, 5, 32, 3]
const resout=[]
for(let i=0; i<x.length; i++){
    console.log(i, x[i])
    const k = x[i];
    const f =new Circle(k)
    resout.push(f)
    resout.push(new Square(k))
    resout.push(new Rektanable(k, k/2))
    

}
console.log(resout.length)
for(let i=0; i<resout.length; i++){
const g=resout[i]
    console.log(
        "Я " + g.getName() + ", моя площадь " + g.getArea().toString()+'\n',
    )
}
