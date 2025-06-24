export interface ApiResult<Type> {
    (arg: Type): Type

    status: number
    data: Type
}